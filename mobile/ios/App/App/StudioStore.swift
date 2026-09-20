import Foundation
import Combine
import UIKit

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
    init(_ value: [String: Any]) {
        id = String(describing: value["id"] ?? value["filename"] ?? "unknown")
        title = studioText(value["title"], fallback: studioText(value["filename"], fallback: "Publication"))
        status = studioText(value["status"], fallback: "unknown")
        platforms = (value["platforms"] as? [String] ?? []).joined(separator: " · ")
        detail = studioText(value["error"], fallback: studioText(value["detail"]))
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
    @Published var username = "lachlanchen"
    @Published var signingIn = false
    @Published var videos: [StudioVideo] = []
    @Published var jobs: [StudioJob] = []
    @Published var loadingVideos = false
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

    init() {
        images.countLimit = 80
        signedIn = api.identity != nil
        username = api.identity?.username ?? "lachlanchen"
        if let bytes = try? Data(contentsOf: StudioFiles.pendingURL) {
            pending = try? JSONDecoder().decode(PendingStudioUpload.self, from: bytes)
            if pending != nil { uploadMessage = "Your video is ready to resume." }
        }
        if let bytes = try? Data(contentsOf: StudioFiles.directory.appendingPathComponent("library.json")) {
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

    func login(password: String) async {
        signingIn = true; error = nil
        defer { signingIn = false }
        do {
            try await api.signIn(username: username.trimmingCharacters(in: .whitespaces), password: password)
            signedIn = true
            await refreshVideos()
        } catch { report(error) }
    }

    func logout() async {
        pauseUpload()
        do {
            try await api.signOut()
            signedIn = false; error = nil; videos = []; jobs = []; images.removeAllObjects()
            try? FileManager.default.removeItem(at: StudioFiles.directory.appendingPathComponent("library.json"))
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
            try? JSONEncoder().encode(videos).write(to: StudioFiles.directory.appendingPathComponent("library.json"), options: [.atomic, .completeFileProtectionUntilFirstUserAuthentication])
            error = nil
        } catch { report(error) }
    }

    func refreshJobs() async {
        guard signedIn else { return }
        do {
            let result = try await api.json("/api/autopublish/queue")
            if studioText(result["status"]) == "unavailable" { throw StudioFailure(message: "The publication queue is temporarily unavailable.", status: 503) }
            jobs = (result["jobs"] as? [[String: Any]] ?? []).map(StudioJob.init)
            error = nil
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
        try JSONEncoder().encode(staged).write(to: StudioFiles.pendingURL, options: [.atomic, .completeFileProtectionUntilFirstUserAuthentication])
        pending = staged; uploadedVideo = nil; uploadProgress = 0; uploadMessage = "Ready to upload."
    }

    func discardUpload() {
        guard !uploading, let pending else { return }
        try? FileManager.default.removeItem(at: StudioFiles.directory.appendingPathComponent(pending.localName))
        try? FileManager.default.removeItem(at: StudioFiles.pendingURL)
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
        try JSONEncoder().encode(value).write(to: StudioFiles.pendingURL, options: [.atomic, .completeFileProtectionUntilFirstUserAuthentication])
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
            try? FileManager.default.removeItem(at: StudioFiles.pendingURL)
        }
        pending = nil
        await refreshVideos()
        uploadedVideo = videos.first(where: { $0.id == id })
    }
}
