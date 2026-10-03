import Foundation
import Combine
import UIKit
import UserNotifications

struct StudioVideo: Identifiable, Hashable, Codable {
    let id: Int
    let title: String
    let media: String?
    let poster: String?
    let created: String
    init?(_ value: [String: Any]) {
        guard let id = value["id"] as? Int else { return nil }
        self.id = id
        title = studioText(value["title"], fallback: "Video \(id)")
        media = (value["preview_media_url"] ?? value["media_url"]) as? String
        poster = value["preview_image_url"] as? String
        created = studioText(value["created_at"]).prefix(16).replacingOccurrences(of: "T", with: " ")
    }
}

struct StudioJob: Identifiable {
    let id: String
    let title: String
    let status: String
    let platforms: String
    let detail: String
    let videoID: Int?
    let attentionMessage: String?
    let attentionURL: String?
    init(_ value: [String: Any]) {
        id = String(describing: value["id"] ?? value["filename"] ?? "unknown")
        title = studioText(value["title"], fallback: studioText(value["filename"], fallback: "Publication"))
        status = studioText(value["status"], fallback: "unknown")
        platforms = (value["platforms"] as? [String] ?? []).joined(separator: " · ")
        detail = studioText(value["error"], fallback: studioText(value["detail"]))
        videoID = value["video_id"] as? Int
        let attention = value["attention"] as? [String: Any]
        attentionMessage = attention?["status"] as? String == "required" ? studioText(attention?["message"], fallback: "Login or verification required") : nil
        attentionURL = attentionMessage == nil ? nil : attention?["artifact_url"] as? String
    }
}

struct PendingStudioUpload: Codable {
    let localName: String
    let filename: String
    let size: Int64
    var uploadID: String?
}

enum StudioFiles {
    static var directory: URL {
        let root = FileManager.default.urls(for: .applicationSupportDirectory, in: .userDomainMask)[0].appendingPathComponent("Studio", isDirectory: true)
        try? FileManager.default.createDirectory(at: root, withIntermediateDirectories: true)
        var url = root
        var values = URLResourceValues(); values.isExcludedFromBackup = true
        try? url.setResourceValues(values)
        return url
    }
    static var pendingURL: URL { directory.appendingPathComponent("upload.json") }
    static func copyVideo(_ source: URL) throws -> PendingStudioUpload {
        let scoped = source.startAccessingSecurityScopedResource()
        defer { if scoped { source.stopAccessingSecurityScopedResource() } }
        guard ["mp4", "mov", "m4v", "webm"].contains(source.pathExtension.lowercased()) else {
            throw StudioFailure(message: "Choose an MP4, MOV, M4V or WebM video.", status: 0)
        }
        let name = UUID().uuidString + "." + source.pathExtension
        let destination = directory.appendingPathComponent(name)
        try FileManager.default.copyItem(at: source, to: destination)
        let size = (try FileManager.default.attributesOfItem(atPath: destination.path)[.size] as? NSNumber)?.int64Value ?? 0
        guard size > 0, size <= 10 * 1024 * 1024 * 1024 else {
            try? FileManager.default.removeItem(at: destination)
            throw StudioFailure(message: "Choose a video between 1 byte and 10 GB.", status: 0)
        }
        return PendingStudioUpload(localName: name, filename: source.lastPathComponent, size: size)
    }
}

@MainActor
final class StudioStore: ObservableObject {
    let api = StudioAPI()
    @Published var signedIn = false
    @Published var username = ""
    @Published var signingIn = false
    @Published var switchingWorkspace = false
    @Published var workspaceMode = "owner"
    @Published var isAdmin = false
    @Published var publishingEnabled = false
    @Published var invitationURL: String?
    @Published var videos: [StudioVideo] = []
    @Published var jobs: [StudioJob] = []
    @Published var loadingVideos = false
    @Published var hiddenVideos: [StudioVideo] = []
    @Published var changingVisibility = Set<Int>()
    @Published var error: String?
    @Published var pending: PendingStudioUpload?
    @Published var uploading = false
    @Published var preparingFile = false
    @Published var uploadProgress: Double = 0
    @Published var uploadMessage = ""
    @Published var uploadedVideo: StudioVideo?
    private var uploadTask: Task<Void, Never>?
    private var backgroundTask: UIBackgroundTaskIdentifier = .invalid
    private let images = NSCache<NSString, UIImage>()
    func enableLoginNotifications() async {
        do { _ = try await UNUserNotificationCenter.current().requestAuthorization(options: [.alert, .badge, .sound]) }
        catch { report(error) }
    }
    private func notifyLoginAttention() async {
        let center = UNUserNotificationCenter.current()
        let context = api.contextKey
        guard await center.notificationSettings().authorizationStatus == .authorized else { return }
        guard signedIn, context == api.contextKey else { return }
        let file = api.privateFile("notified-jobs.json")
        var seen = ((try? Data(contentsOf: file)).flatMap { try? JSONDecoder().decode([String].self, from: $0) }) ?? []
        for job in jobs where job.attentionMessage != nil {
            // Generic lock-screen text; do not put QR codes, media or credentials in notifications.
            let key = job.id + ":" + job.status
            if seen.contains(key) { continue }
            let content = UNMutableNotificationContent()
            content.title = "LazyEdit Studio"
            content.body = StudioStrings.text("Login or verification required")
            content.sound = .default
            content.userInfo = ["studioContext": context]
            do { try await center.add(UNNotificationRequest(identifier: context+":"+job.id, content: content, trigger: nil)); seen.append(key) }
            catch { continue }
        }
        try? JSONEncoder().encode(Array(seen.suffix(256))).write(to: file, options: [.atomic, .completeFileProtectionUntilFirstUserAuthentication])
    }

    init() {
        images.countLimit = 80
        signedIn = api.identity != nil
        username = api.identity?.username ?? ""
        workspaceMode = api.workspaceMode
        if let bytes = try? Data(contentsOf: api.privateFile("upload.json")) {
            pending = try? JSONDecoder().decode(PendingStudioUpload.self, from: bytes)
            if pending != nil { uploadMessage = "Your video is ready to resume." }
        }
        if let bytes = try? Data(contentsOf: api.privateFile("library.json")) {
            videos = (try? JSONDecoder().decode([StudioVideo].self, from: bytes)) ?? []
        }
    }

    func report(_ failure: Error) {
        if failure is CancellationError || (failure as? URLError)?.code == .cancelled { return }
        error = failure.localizedDescription
        if (failure as? StudioFailure)?.status == 401 {
            api.clearSession(); signedIn = false
        }
    }

    func login(password: String, workspace: Bool = false, invitation: String? = nil) async {
        signingIn = true; error = nil
        defer { signingIn = false }
        do {
            try await api.signIn(username: username.trimmingCharacters(in: .whitespaces), password: password, workspace: workspace, invitation: invitation)
            videos = []; jobs = []; images.removeAllObjects(); workspaceMode = api.workspaceMode
            signedIn = true; publishingEnabled = false
            pending = (try? Data(contentsOf: api.privateFile("upload.json"))).flatMap { try? JSONDecoder().decode(PendingStudioUpload.self, from: $0) }
            await refreshAccount()
            await refreshVideos()
        } catch { report(error) }
    }
    func refreshAccount() async {
        guard signedIn else { return }
        do {
            let account = try await api.json("/auth/me")
            publishingEnabled = (account["capabilities"] as? [String: Bool])?["publishing"] ?? (workspaceMode == "owner" && (account["scopes"] as? [String] ?? []).contains("publication.publish"))
        }
        catch { publishingEnabled = false }
        do { isAdmin = try await api.json("/accounts/account")["role"] as? String == "admin" }
        catch { isAdmin = false }
        do {
            let catalog = try await api.json("/accounts/billing/catalog")
            billingAvailable = catalog["enabled"] as? Bool == true && (catalog["providers"] as? [String] ?? []).contains("apple")
        } catch { billingAvailable = false }
    }
    @Published var billingAvailable = false
    func createInvitation() async {
        do { invitationURL = try await api.json("/accounts/invite", method: "POST", body: [:])["url"] as? String }
        catch { report(error) }
    }
    func switchWorkspace(_ mode: String) async {
        guard !switchingWorkspace, !uploading, pending == nil, !preparingFile else {
            error = "Finish or remove your current upload before switching workspaces."; return
        }
        switchingWorkspace = true; error = nil
        defer { switchingWorkspace = false }
        do {
            publishingEnabled = false
            try await api.switchMode(mode)
            workspaceMode = api.workspaceMode; videos = []; jobs = []; hiddenVideos = []; uploadedVideo = nil; images.removeAllObjects(); invitationURL = nil
            await refreshVideos(); await refreshAccount()
        } catch { workspaceMode = api.workspaceMode; videos = []; jobs = []; images.removeAllObjects(); report(error) }
    }

    func logout() async {
        pauseUpload()
        let libraryFile = api.privateFile("library.json")
        do {
            try await api.signOut()
            signedIn = false; error = nil; videos = []; jobs = []; images.removeAllObjects()
            try? FileManager.default.removeItem(at: libraryFile)
            isAdmin = false; publishingEnabled = false; invitationURL = nil
        } catch { report(error) }
    }

    func deleteAccount(password: String) async {
        guard workspaceMode == "workspace", !isAdmin, !uploading, !preparingFile else { return }
        do {
            _ = try await api.json("/accounts/delete", method: "POST", body: ["confirm": username, "password": password])
            discardUpload()
            for name in ["library.json", "notified-jobs.json"] { try? FileManager.default.removeItem(at: api.privateFile(name)) }
            api.clearSession(); signedIn = false; videos = []; jobs = []; hiddenVideos = []; images.removeAllObjects()
            invitationURL = nil; error = nil
        } catch { report(error) }
    }

    @Published var oauthProviders: [String] = []
    @Published var linkedProviders: [String] = []
    func refreshSignInProviders() async {
        oauthProviders = (try? await api.json("/accounts/oauth/providers")["providers"] as? [String]) ?? []
        linkedProviders = signedIn ? (try? await api.json("/accounts/oauth/links")["providers"] as? [String]) ?? [] : []
    }
    func unlinkProvider(_ provider: String, password: String) async {
        do {_ = try await api.json("/accounts/oauth/unlink", method: "POST", body: ["provider": provider, "password": password]); await refreshSignInProviders()}
        catch { report(error) }
    }
    func oauthSignIn(provider: String, password: String? = nil) async {
        guard !signingIn, !uploading, !preparingFile, pending == nil else { return }
        signingIn = true; error = nil
        defer { signingIn = false }
        do {
            try await api.oauthSignIn(provider: provider, password: password)
            username = api.identity?.username ?? ""; signedIn = true; workspaceMode = api.workspaceMode
            videos = []; jobs = []; images.removeAllObjects()
            await refreshAccount(); await refreshVideos()
        } catch { report(error) }
    }

    func refreshVideos() async {
        guard signedIn, !loadingVideos else { return }
        loadingVideos = true
        defer { loadingVideos = false }
        do {
            let value = try await api.json("/api/videos")
            guard let rows = value["videos"] as? [[String: Any]] else { throw StudioFailure(message: "Could not read your library.", status: 0) }
            videos = rows.compactMap(StudioVideo.init)
            try? JSONEncoder().encode(videos).write(to: api.privateFile("library.json"), options: [.atomic, .completeFileProtectionUntilFirstUserAuthentication])
            error = nil
        } catch { report(error) }
    }

    func refreshJobs() async {
        guard signedIn else { return }
        let context = api.contextKey
        do {
            let result = try await api.json("/api/autopublish/queue")
            guard signedIn, context == api.contextKey else { return }
            if studioText(result["status"]) == "unavailable" { throw StudioFailure(message: "The publication queue is temporarily unavailable.", status: 503) }
            jobs = (result["jobs"] as? [[String: Any]] ?? []).map(StudioJob.init)
            await notifyLoginAttention()
            error = nil
        } catch { report(error) }
    }

    func refreshHidden() async {
        do {
            let result = try await api.json("/api/videos?hidden=true")
            hiddenVideos = (result["videos"] as? [[String: Any]] ?? []).compactMap(StudioVideo.init)
        } catch { report(error) }
    }

    func setHidden(_ video: StudioVideo, hidden: Bool) async {
        guard !changingVisibility.contains(video.id) else { return }
        changingVisibility.insert(video.id)
        defer { changingVisibility.remove(video.id) }
        do {
            _ = try await api.json("/v1/studio/videos/\(video.id)/visibility", method: "POST", body: ["hidden": hidden])
            await refreshVideos()
            await refreshHidden()
        } catch { report(error) }
    }

    func thumbnail(_ path: String) async -> UIImage? {
        if let cached = images.object(forKey: path as NSString) { return cached }
        guard let bytes = try? await api.data(path), let image = UIImage(data: bytes) else { return nil }
        images.setObject(image, forKey: path as NSString)
        return image
    }

    func prepareFile(_ source: URL) async {
        guard !uploading, !preparingFile, pending == nil else { return }
        preparingFile = true; error = nil
        defer { preparingFile = false }
        do {
            let staged = try await Task.detached(priority: .userInitiated) { try StudioFiles.copyVideo(source) }.value
            try accept(staged)
        } catch { report(error) }
    }

    func accept(_ staged: PendingStudioUpload) throws {
        guard pending == nil else {
            try? FileManager.default.removeItem(at: StudioFiles.directory.appendingPathComponent(staged.localName))
            throw StudioFailure(message: "Finish or remove your current upload first.", status: 0)
        }
        try JSONEncoder().encode(staged).write(to: api.privateFile("upload.json"), options: [.atomic, .completeFileProtectionUntilFirstUserAuthentication])
        pending = staged; uploadedVideo = nil; uploadProgress = 0; uploadMessage = "Ready to upload."
    }

    func discardUpload() {
        guard !uploading, let pending else { return }
        try? FileManager.default.removeItem(at: StudioFiles.directory.appendingPathComponent(pending.localName))
        try? FileManager.default.removeItem(at: api.privateFile("upload.json"))
        self.pending = nil; uploadProgress = 0; uploadMessage = ""
    }

    func pauseUpload() { uploadTask?.cancel() }

    func beginUpload() {
        guard signedIn, !uploading, pending != nil else { return }
        uploading = true; error = nil; uploadMessage = "Connecting…"
        backgroundTask = UIApplication.shared.beginBackgroundTask(withName: "Finish Studio upload chunk") { [weak self] in
            Task { @MainActor in self?.pauseUpload() }
        }
        uploadTask = Task { [weak self] in
            guard let self else { return }
            defer {
                uploading = false; uploadTask = nil
                if backgroundTask != .invalid { UIApplication.shared.endBackgroundTask(backgroundTask); backgroundTask = .invalid }
            }
            do { try await upload() }
            catch is CancellationError { uploadMessage = "Paused. Resume whenever you are ready." }
            catch {
                uploadMessage = "Upload paused. Resume to continue from the saved position."
                report(error)
            }
        }
    }

    private func savePending(_ value: PendingStudioUpload) throws {
        try JSONEncoder().encode(value).write(to: api.privateFile("upload.json"), options: [.atomic, .completeFileProtectionUntilFirstUserAuthentication])
        pending = value
    }

    private func upload() async throws {
        guard var current = pending else { return }
        let source = StudioFiles.directory.appendingPathComponent(current.localName)
        let handle = try FileHandle(forReadingFrom: source)
        defer { try? handle.close() }
        if current.uploadID == nil {
            let value = try await api.json("/v1/studio/uploads", method: "POST", body: ["filename": current.filename, "title": current.filename, "size": current.size])
            guard let id = value["uploadId"] as? String else { throw StudioFailure(message: "Upload could not be created.", status: 0) }
            current.uploadID = id; try savePending(current)
        }
        let id = current.uploadID!
        let position: [String: Any]
        do { position = try await api.json("/v1/studio/upload?uploadId=\(id)") }
        catch let failure as StudioFailure where failure.status == 404 {
            current.uploadID = nil; try savePending(current)
            throw StudioFailure(message: "The saved upload expired. Tap Resume to start a new upload.", status: 404)
        }
        if let receipt = position["receipt"] as? [String: Any] { try await complete(receipt); return }
        var offset = (position["offset"] as? NSNumber)?.int64Value ?? 0
        guard offset >= 0, offset <= current.size else { throw StudioFailure(message: "Studio returned an invalid upload position.", status: 0) }
        while offset < current.size {
            try Task.checkCancellation()
            try handle.seek(toOffset: UInt64(offset))
            guard let bytes = try handle.read(upToCount: min(8 * 1024 * 1024, Int(current.size - offset))), !bytes.isEmpty else {
                throw StudioFailure(message: "The selected video could not be read.", status: 0)
            }
            let confirmed = offset, total = current.size
            uploadMessage = "Uploading \(current.filename)"
            let next = try await api.chunk(uploadID: id, offset: offset, bytes: bytes) { [weak self] sent in
                Task { @MainActor in self?.uploadProgress = min(1, Double(confirmed + sent) / Double(total)) }
            }
            guard next == offset + Int64(bytes.count) else { throw StudioFailure(message: "Upload position changed. Resume to check it.", status: 0) }
            offset = next; uploadProgress = Double(offset) / Double(current.size)
        }
        try Task.checkCancellation()
        uploadMessage = "Checking your video…"
        let receipt = try await api.json("/v1/studio/upload-complete", method: "POST", body: ["uploadId": id])
        try await complete(receipt)
    }

    private func complete(_ receipt: [String: Any]) async throws {
        guard let id = (receipt["videoId"] ?? receipt["video_id"]) as? Int else { throw StudioFailure(message: "Upload confirmation is missing. Resume to check it.", status: 0) }
        uploadProgress = 1; uploadMessage = "Added to your Studio."
        if let current = pending {
            try? FileManager.default.removeItem(at: StudioFiles.directory.appendingPathComponent(current.localName))
            try? FileManager.default.removeItem(at: api.privateFile("upload.json"))
        }
        pending = nil
        await refreshVideos()
        uploadedVideo = videos.first(where: { $0.id == id })
    }
}
