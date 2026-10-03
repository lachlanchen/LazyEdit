import SwiftUI
import StoreKit
import AVKit
import PhotosUI
import UniformTypeIdentifiers
import WebKit

private let studioTint = Color(red: 0.13, green: 0.37, blue: 0.29)

// Keep the same native screens on Monterey's Mac Catalyst and newer phones.
struct StudioNavigation<Content: View>: View {
    private let content: Content
    init(@ViewBuilder content: () -> Content) { self.content = content() }
    var body: some View {
        if #available(iOS 16, macCatalyst 16, *) { NavigationStack { content } }
        else { NavigationView { content }.navigationViewStyle(.stack) }
    }
}

struct StudioShareButton: View {
    let url: URL
    @State private var sharing = false
    var body: some View {
        if #available(iOS 16, macCatalyst 16, *) {
            ShareLink(item: url) { Label(StudioStrings.text("Share invitation"), systemImage: "square.and.arrow.up") }
        } else {
            Button { sharing = true } label: { Label(StudioStrings.text("Share invitation"), systemImage: "square.and.arrow.up") }
                .sheet(isPresented: $sharing) { StudioShareSheet(url: url) }
        }
    }
}
private struct StudioShareSheet: UIViewControllerRepresentable {
    let url: URL
    func makeUIViewController(context: Context) -> UIActivityViewController { UIActivityViewController(activityItems: [url], applicationActivities: nil) }
    func updateUIViewController(_ controller: UIActivityViewController, context: Context) {}
}

struct StudioLabeledValue: View {
    let title: String
    let value: String
    init(_ title: String, value: String) { self.title = title; self.value = value }
    var body: some View { HStack { Text(title); Spacer(); Text(value).foregroundStyle(.secondary).multilineTextAlignment(.trailing) } }
}
struct StudioContextInput: View {
    @Binding var text: String
    var body: some View {
        if #available(iOS 16, macCatalyst 16, *) {
            TextField(StudioStrings.text("Story, names, technical terms or reference script"), text: $text, axis: .vertical).lineLimit(4...10)
        } else {
            VStack(alignment: .leading) {
                Text(StudioStrings.text("Story, names, technical terms or reference script")).font(.caption).foregroundStyle(.secondary)
                TextEditor(text: $text).frame(minHeight: 100, maxHeight: 220)
            }
        }
    }
}
extension View {
    @ViewBuilder func studioKeyboardDismissal() -> some View {
        if #available(iOS 16, macCatalyst 16, *) { self.scrollDismissesKeyboard(.interactively) }
        else { self }
    }
}

struct NativeStudioRoot: View {
    @StateObject private var store = StudioStore()
    @State private var tab = 0
    @AppStorage("studio.interfaceLanguage") private var interfaceLanguage = ""
    @Environment(\.scenePhase) private var scenePhase
    var body: some View {
        Group {
            if store.signedIn {
                TabView(selection: $tab) {
                    StudioLibraryView(onUpload: { tab = 1 }).tabItem { Label(StudioStrings.text("Studio"), systemImage: "square.stack") }.tag(0)
                    StudioUploadView().tabItem { Label(StudioStrings.text("Upload"), systemImage: "plus.circle") }.tag(1)
                    StudioJobsView().tabItem { Label(StudioStrings.text("Activity"), systemImage: "clock.arrow.circlepath") }.badge(store.jobs.filter { $0.attentionMessage != nil }.count).tag(2)
                    StudioAccountView().tabItem { Label(StudioStrings.text("Account"), systemImage: "person.crop.circle") }.tag(3)
                }.id(store.workspaceMode).disabled(store.switchingWorkspace)
            } else { StudioLoginView() }
        }
        .id(interfaceLanguage)
        .environment(\.layoutDirection, StudioStrings.language == "ar" ? .rightToLeft : .leftToRight)
        .tint(studioTint)
        .environmentObject(store)
        .onReceive(NotificationCenter.default.publisher(for: .studioLoginAttention)) { notification in
            if store.signedIn, notification.userInfo?["studioContext"] as? String == store.api.contextKey { tab = 2 }
        }
        .task(id: "\(store.signedIn)-\(store.api.contextKey)-\(scenePhase)") {
            guard store.signedIn, scenePhase == .active else { return }
            while !Task.isCancelled { await store.refreshJobs(); do { try await Task.sleep(nanoseconds: 30_000_000_000) } catch { break } }
        }
    }
}

struct StudioLoginView: View {
    @EnvironmentObject private var store: StudioStore
    @State private var password = ""
    @State private var workspace = false
    @State private var register = false
    @State private var invitation = ""
    var body: some View {
        StudioNavigation {
            ScrollView {
                VStack(alignment: .leading, spacing: 24) {
                    Image("StudioMark").resizable().frame(width: 76, height: 76).clipShape(RoundedRectangle(cornerRadius: 19))
                    VStack(alignment: .leading, spacing: 8) {
                        Text(StudioStrings.text("Your stories.\nYour Studio.")).font(.system(size: 38, weight: .bold, design: .rounded))
                        Text(StudioStrings.text("A quiet space to edit, prepare and share your videos.")).foregroundStyle(.secondary)
                    }
                    StudioLanguagePicker().disabled(store.signingIn)
                    VStack(spacing: 16) {
                        if store.username.trimmingCharacters(in: .whitespaces) == "lachlanchen" {
                            Picker(StudioStrings.text("Workspace"), selection: $workspace) {
                                Text(StudioStrings.text("Existing Pi")).tag(false); Text(StudioStrings.text("Private workspace")).tag(true)
                            }.pickerStyle(.segmented)
                        }
                        if workspace || store.username.trimmingCharacters(in: .whitespaces) != "lachlanchen" {
                            Toggle(StudioStrings.text("Create account with invitation"), isOn: $register)
                            if register { TextField(StudioStrings.text("Invitation code"), text: $invitation).textInputAutocapitalization(.never).autocorrectionDisabled() }
                        }
                        TextField(StudioStrings.text("Username"), text: $store.username).textContentType(.username).textInputAutocapitalization(.never).autocorrectionDisabled().accessibilityIdentifier("studio.username")
                        SecureField(StudioStrings.text("Password"), text: $password).textContentType(.password).submitLabel(.go).accessibilityIdentifier("studio.password")
                            .onSubmit { signIn() }
                    }.textFieldStyle(.roundedBorder)
                    StudioErrorBanner()
                    Button(action: signIn) {
                        HStack { Spacer(); if store.signingIn { ProgressView().tint(.white) }; Text(StudioStrings.text(store.signingIn ? "Signing in…" : "Sign in")).bold(); Spacer() }.padding(.vertical, 7)
                    }.buttonStyle(.borderedProminent).disabled(store.signingIn || password.isEmpty || store.username.isEmpty).accessibilityIdentifier("studio.signIn")
                    ForEach(store.oauthProviders, id: \.self) { provider in
                        Button(StudioStrings.text(provider == "apple" ? "Continue with Apple" : "Continue with Google")) { Task { await store.oauthSignIn(provider: provider) } }.buttonStyle(.bordered).disabled(store.signingIn)
                    }
                    Text("edit.lazying.art").font(.footnote).foregroundStyle(.secondary)
                }.padding(28).padding(.top, 48)
            }.background(Color(uiColor: .systemGroupedBackground)).task { await store.refreshSignInProviders() }
        }
    }
    private func signIn() {
        guard !store.signingIn, !password.isEmpty else { return }
        UIApplication.shared.sendAction(#selector(UIResponder.resignFirstResponder), to: nil, from: nil, for: nil)
        let value = password
        let usePrivate = workspace || store.username.trimmingCharacters(in: .whitespaces) != "lachlanchen"
        Task { await store.login(password: value, workspace: usePrivate, invitation: usePrivate && register ? invitation : nil); if store.signedIn { password = "" } }
    }
}

struct StudioErrorBanner: View {
    @EnvironmentObject private var store: StudioStore
    var body: some View {
        if let error = store.error {
            HStack(alignment: .top) {
                Image(systemName: "exclamationmark.circle")
                Text(error).font(.subheadline)
                Spacer(minLength: 4)
                Button { store.error = nil } label: { Image(systemName: "xmark") }.accessibilityLabel("Dismiss message")
            }.padding().background(Color.orange.opacity(0.12), in: RoundedRectangle(cornerRadius: 12))
        }
    }
}

struct StudioThumbnail: View {
    @EnvironmentObject private var store: StudioStore
    let video: StudioVideo
    @State private var image: UIImage?
    var body: some View {
        ZStack {
            RoundedRectangle(cornerRadius: 12).fill(studioTint.opacity(0.1))
            if let image { Image(uiImage: image).resizable().scaledToFill() }
            else { Image(systemName: "play.rectangle").font(.title2).foregroundStyle(studioTint) }
        }.frame(width: 86, height: 72).clipShape(RoundedRectangle(cornerRadius: 12))
            .task(id: video.poster) { if let path = video.poster { image = await store.thumbnail(path) } }
    }
}

struct StudioLibraryView: View {
    @EnvironmentObject private var store: StudioStore
    let onUpload: () -> Void
    @State private var search = ""
    @State private var showHidden = false
    private var filtered: [StudioVideo] { search.isEmpty ? store.videos : store.videos.filter { $0.title.localizedCaseInsensitiveContains(search) } }
    var body: some View {
        StudioNavigation {
            List {
                if store.error != nil { StudioErrorBanner().listRowSeparator(.hidden) }
                if store.loadingVideos && store.videos.isEmpty { ProgressView(StudioStrings.text("Opening your library…")) }
                if !store.loadingVideos && store.videos.isEmpty {
                    VStack(spacing: 14) {
                        Image(systemName: "film.stack").font(.largeTitle)
                        Text(StudioStrings.text("Your next story starts here")).font(.headline)
                        Text(StudioStrings.text("Choose a video from Photos or Files to add it to your Studio.")).foregroundStyle(.secondary).multilineTextAlignment(.center)
                        Button(StudioStrings.text("Add a video"), action: onUpload).buttonStyle(.borderedProminent)
                    }.padding(.vertical, 32).frame(maxWidth: .infinity)
                }
                ForEach(filtered) { video in
                    NavigationLink(destination: StudioVideoView(video: video)) {
                        HStack(spacing: 14) {
                            StudioThumbnail(video: video)
                            VStack(alignment: .leading, spacing: 7) {
                                Text(video.title).font(.headline).lineLimit(2)
                                Text(video.created).font(.caption).foregroundStyle(.secondary)
                            }
                        }.padding(.vertical, 5)
                    }
                    .swipeActions(edge: .trailing, allowsFullSwipe: false) {
                        Button { Task { await store.setHidden(video, hidden: true) } } label: { Label(StudioStrings.text("Remove"), systemImage: "archivebox") }
                            .tint(.orange).disabled(store.changingVisibility.contains(video.id))
                    }
                }
            }
            .navigationTitle(StudioStrings.text("Your Studio"))
            .searchable(text: $search, prompt: "Find a video")
            .toolbar {
                ToolbarItem(placement: .navigationBarLeading) { Button { showHidden = true } label: { Image(systemName: "archivebox") }.accessibilityLabel("Removed videos") }
                ToolbarItem(placement: .navigationBarTrailing) { Button(action: onUpload) { Image(systemName: "plus") }.accessibilityLabel("Add video") }
            }
            .sheet(isPresented: $showHidden) { StudioRemovedVideos() }
            .refreshable { await store.refreshVideos() }
            .task { await store.refreshVideos() }
        }
    }
}

struct StudioUploadView: View {
    @EnvironmentObject private var store: StudioStore
    @State private var files = false
    @State private var photos = false
    @State private var remove = false
    var body: some View {
        StudioNavigation {
            ScrollView {
                VStack(alignment: .leading, spacing: 24) {
                    Text(StudioStrings.text("Bring your next story.")).font(.title2.bold())
                    Text(StudioStrings.text("Your original video stays on your device. Studio prepares a separate copy for editing and publication.")).foregroundStyle(.secondary)
                    HStack(spacing: 14) {
                        Button { photos = true } label: { Label(StudioStrings.text("Photos"), systemImage: "photo.on.rectangle").frame(maxWidth: .infinity).padding(.vertical, 12) }
                        Button { files = true } label: { Label(StudioStrings.text("Files"), systemImage: "folder").frame(maxWidth: .infinity).padding(.vertical, 12) }
                    }.buttonStyle(.bordered).disabled(store.pending != nil || store.preparingFile || store.uploading)
                    if store.preparingFile { ProgressView(StudioStrings.text("Preparing your video…")) }
                    StudioErrorBanner()
                    if let pending = store.pending {
                        VStack(alignment: .leading, spacing: 14) {
                            Label(pending.filename, systemImage: "video").font(.headline).lineLimit(2)
                            Text(ByteCountFormatter.string(fromByteCount: pending.size, countStyle: .file)).foregroundStyle(.secondary)
                            ProgressView(value: store.uploadProgress)
                            Text(StudioStrings.text(store.uploadMessage)).font(.subheadline).foregroundStyle(.secondary)
                            if store.uploading { Button(StudioStrings.text("Pause upload")) { store.pauseUpload() }.buttonStyle(.bordered) }
                            else {
                                HStack {
                                    Button(pending.uploadID == nil ? "Upload video" : "Resume upload") { store.beginUpload() }.buttonStyle(.borderedProminent).accessibilityIdentifier("studio.upload")
                                    Spacer()
                                    Button(StudioStrings.text("Remove"), role: .destructive) { remove = true }
                                }
                            }
                        }.padding(20).background(Color(uiColor: .secondarySystemGroupedBackground), in: RoundedRectangle(cornerRadius: 18))
                    }
                    if let video = store.uploadedVideo {
                        Label(StudioStrings.text("Added to your Studio"), systemImage: "checkmark.circle.fill").foregroundStyle(studioTint)
                        NavigationLink("Open video", destination: StudioVideoView(video: video)).buttonStyle(.borderedProminent)
                    }
                    Text(StudioStrings.text("Uploads can resume after interruptions. Keep the app open for the fastest transfer.")).font(.footnote).foregroundStyle(.secondary)
                }.padding(24)
            }.background(Color(uiColor: .systemGroupedBackground))
                .navigationTitle(StudioStrings.text("Upload"))
                .fileImporter(isPresented: $files, allowedContentTypes: [.movie], allowsMultipleSelection: false) { result in
                    switch result {
                    case .success(let urls): if let source = urls.first { Task { await store.prepareFile(source) } }
                    case .failure(let error): store.report(error)
                    }
                }
                .sheet(isPresented: $photos) {
                    StudioPhotoPicker { result in
                        photos = false
                        switch result {
                        case .success(let staged): do { try store.accept(staged) } catch { store.report(error) }
                        case .failure(let error): store.report(error)
                        }
                        store.preparingFile = false
                    } onLoading: { store.preparingFile = true; photos = false }
                }
                .confirmationDialog(StudioStrings.text("Remove this local upload copy?"), isPresented: $remove) {
                    Button(StudioStrings.text("Remove upload copy"), role: .destructive) { store.discardUpload() }
                } message: { Text(StudioStrings.text("Your original video stays in Photos or Files. Any unfinished server upload expires automatically.")) }
        }
    }
}

struct StudioVideoView: View {
    @EnvironmentObject private var store: StudioStore
    @Environment(\.scenePhase) private var scenePhase
    let video: StudioVideo
    @State private var player: AVPlayer?
    @State private var editor = false
    @State private var composer = false
    @State private var steps: [(String, String)] = []
    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 22) {
                if let player { VideoPlayer(player: player).frame(height: 280).clipShape(RoundedRectangle(cornerRadius: 16)) }
                else {
                    Button(action: preview) {
                        VStack(spacing: 12) { Image(systemName: "play.circle.fill").font(.system(size: 48)); Text(StudioStrings.text("Preview video")) }.frame(maxWidth: .infinity).frame(height: 200)
                    }.background(studioTint.opacity(0.08), in: RoundedRectangle(cornerRadius: 16))
                }
                Text(video.title).font(.title2.bold())
                Text(video.created).foregroundStyle(.secondary).font(.subheadline)
                StudioErrorBanner()
                Button { player?.pause(); composer = true } label: { Label(StudioStrings.text("Prepare & publish"), systemImage: "slider.horizontal.3").frame(maxWidth: .infinity).padding(.vertical, 8) }.buttonStyle(.borderedProminent).accessibilityIdentifier("studio.compose")
                Button(StudioStrings.text("Full editor · subtitles, metadata & cover")) { player?.pause(); editor = true }
                if !steps.isEmpty {
                    Text(StudioStrings.text("Processing")).font(.headline)
                    ForEach(steps, id: \.0) { item in HStack { Text(item.0); Spacer(); Text(item.1.capitalized).foregroundStyle(.secondary) }.font(.subheadline) }
                }
            }.padding(24)
        }.navigationTitle(StudioStrings.text("Video")).navigationBarTitleDisplayMode(.inline)
            .task { await loadStatus() }
            .refreshable { await loadStatus() }
            .onDisappear { player?.pause() }
            .onChange(of: scenePhase) { phase in if phase != .active { player?.pause() } }
            .sheet(isPresented: $editor) { StudioEditorSheet(path: "/editor?videoId=\(video.id)") }
            .sheet(isPresented: $composer, onDismiss: { Task { await loadStatus() } }) { StudioComposerView(video: video) }
    }
    private func preview() {
        guard let media = video.media else { return }
        do {
            let asset = AVURLAsset(url: try store.api.url(media), options: [AVURLAssetHTTPCookiesKey: store.api.webCookies])
            player = AVPlayer(playerItem: AVPlayerItem(asset: asset))
        } catch { store.report(error) }
    }
    private func loadStatus() async {
        do {
            let result = try await store.api.json("/api/videos/\(video.id)/process-status")
            let values = result["steps"] as? [String: [String: Any]] ?? [:]
            let names = [("transcribe", "Transcription"), ("polish", "Subtitle correction"), ("translate", "Translation"), ("burn", "Render"), ("metadata_zh", "Chinese metadata"), ("metadata_en", "English metadata"), ("cover", "Cover")]
            steps = names.map { ($0.1, studioText(values[$0.0]?["status"], fallback: "idle")) }
        } catch { store.report(error) }
    }
}

struct StudioJobsView: View {
    @EnvironmentObject private var store: StudioStore
    @Environment(\.scenePhase) private var scenePhase
    @State private var selectedJob: StudioJob?
    var body: some View {
        StudioNavigation {
            List {
                StudioErrorBanner()
                if store.jobs.isEmpty { Label(StudioStrings.text("No publication tasks to show"), systemImage: "checkmark.circle").foregroundStyle(.secondary) }
                ForEach(store.jobs) { job in
                    VStack(alignment: .leading, spacing: 8) {
                        Text(job.title).font(.headline)
                        Label(job.status.capitalized, systemImage: job.status == "done" ? "checkmark.circle.fill" : "clock").foregroundStyle(job.status == "done" ? studioTint : Color.secondary)
                        Text(job.platforms).font(.caption).foregroundStyle(.secondary)
                        if !job.detail.isEmpty { Text(job.detail).font(.subheadline).foregroundStyle(.secondary) }
                        if let attention = job.attentionMessage { Label(attention, systemImage: "qrcode.viewfinder").foregroundStyle(.orange) }
                        Button(StudioStrings.text(job.attentionMessage == nil ? "View task" : "Open login / verification")) { selectedJob = job }
                    }.padding(.vertical, 8)
                }
            }.navigationTitle(StudioStrings.text("Activity"))
                .sheet(item: $selectedJob) { StudioJobSheet(job: $0) }
                .refreshable { await store.refreshJobs() }
        }
    }
}

struct StudioAccountView: View {
    @EnvironmentObject private var store: StudioStore
    @State private var signOut = false
    @State private var editor = false
    @State private var platformAccounts = false
    @State private var deletion = false
    @State private var deletionPassword = ""
    @State private var linkProvider: String? = nil
    @State private var linkPassword = ""
    @State private var billing = false
    var body: some View {
        StudioNavigation {
            Form {
                Section {
                    HStack(spacing: 14) {
                        Image("StudioMark").resizable().frame(width: 52, height: 52).clipShape(RoundedRectangle(cornerRadius: 13))
                        VStack(alignment: .leading, spacing: 4) { Text(store.username).font(.headline); Text("edit.lazying.art").font(.subheadline).foregroundStyle(.secondary) }
                    }.padding(.vertical, 8)
                }
                Section(StudioStrings.text("Language")) { StudioLanguagePicker().disabled(store.uploading || store.switchingWorkspace) }
                if store.billingAvailable { Section { Button(StudioStrings.text("Plans and billing")) { billing = true } } }
                if !store.oauthProviders.isEmpty {
                    Section(StudioStrings.text("Linked sign-in accounts")) {
                        ForEach(store.oauthProviders, id: \.self) { provider in Button(StudioStrings.text(store.linkedProviders.contains(provider) ? (provider == "apple" ? "Unlink Apple account" : "Unlink Google account") : (provider == "apple" ? "Link Apple account" : "Link Google account"))) { linkProvider = provider } }
                    }
                }
                Section(StudioStrings.text("Workspace")) {
                    Text(StudioStrings.text(store.workspaceMode == "owner" ? "Existing Pi workspace" : "Private Docker workspace"))
                    if store.switchingWorkspace { ProgressView(StudioStrings.text("Opening workspace…")) }
                    if store.isAdmin {
                        Button(StudioStrings.text(store.workspaceMode == "owner" ? "Switch to private Docker workspace" : "Switch to existing Pi workspace")) { Task { await store.switchWorkspace(store.workspaceMode == "owner" ? "workspace" : "owner") } }.disabled(store.switchingWorkspace || store.uploading || store.pending != nil)
                        Button(StudioStrings.text("Create invitation")) { Task { await store.createInvitation() } }
                        if let link = store.invitationURL, let url = URL(string: link) {
                            StudioShareButton(url: url)
                            Text(StudioStrings.text("Single use · expires in 72 hours")).font(.footnote).foregroundStyle(.secondary)
                        }
                    }
                    if store.workspaceMode == "workspace" { Button(StudioStrings.text("Platform accounts")) { platformAccounts = true } }
                }
                Section { Button(StudioStrings.text("Enable login notifications")) { Task { await store.enableLoginNotifications() } }; Button(StudioStrings.text("Open full Studio")) { editor = true }; Link("Privacy", destination: URL(string: "https://edit.lazying.art/privacy")!) }
                Section { StudioErrorBanner(); Button(StudioStrings.text("Sign out"), role: .destructive) { signOut = true } }
                if store.workspaceMode == "workspace" && !store.isAdmin {
                    Section { Button(StudioStrings.text("Delete account"), role: .destructive) { deletion = true }.disabled(store.uploading || store.preparingFile) }
                }
                Section { Text("LazyEdit Studio · \(Bundle.main.object(forInfoDictionaryKey: "CFBundleShortVersionString") as? String ?? "1.0") (\(Bundle.main.object(forInfoDictionaryKey: "CFBundleVersion") as? String ?? ""))").foregroundStyle(.secondary) }
            }.navigationTitle(StudioStrings.text("Account"))
                .sheet(isPresented: $editor) { StudioEditorSheet(path: "/home") }
                .sheet(isPresented: $platformAccounts) { StudioEditorSheet(path: "/platforms") }
                .sheet(isPresented: $billing) { StudioBillingView() }
                .task { await store.refreshAccount(); await store.refreshSignInProviders() }
                .alert(StudioStrings.text("Link sign-in account"), isPresented: Binding(get: {linkProvider != nil}, set: {if !$0 {linkProvider = nil}})) {
                    SecureField(StudioStrings.text("Password"), text: $linkPassword)
                    Button(StudioStrings.text("Cancel"), role: .cancel) { linkProvider = nil; linkPassword = "" }
                    Button(StudioStrings.text("Continue")) { let provider = linkProvider, password = linkPassword; linkProvider = nil; linkPassword = ""; if let provider { Task { if store.linkedProviders.contains(provider) {await store.unlinkProvider(provider, password: password)} else {await store.oauthSignIn(provider: provider, password: password)} } } }
                } message: { Text(StudioStrings.text("Confirm your Studio password, then choose the provider account to link.")) }
                .confirmationDialog(StudioStrings.text("Sign out of Studio?"), isPresented: $signOut) { Button(StudioStrings.text("Sign out"), role: .destructive) { Task { await store.logout() } } }
                .alert(StudioStrings.text("Delete account"), isPresented: $deletion) {
                    SecureField(StudioStrings.text("Password"), text: $deletionPassword)
                    Button(StudioStrings.text("Cancel"), role: .cancel) { deletionPassword = "" }
                    Button(StudioStrings.text("Delete account"), role: .destructive) {
                        let password = deletionPassword; deletionPassword = ""
                        Task { await store.deleteAccount(password: password) }
                    }
                } message: { Text(StudioStrings.text("This permanently removes your private workspace and platform logins. Published posts remain on their platforms. Wait for active work to finish first.")) }
        }
    }
}

struct StudioBillingView: View {
    @EnvironmentObject private var store: StudioStore
    @Environment(\.dismiss) private var dismiss
    @State private var catalog: [String: Any] = [:]
    @State private var products: [Product] = []
    @State private var busy = false
    @State private var message = ""
    private var enabled: Bool { catalog["enabled"] as? Bool == true && (catalog["providers"] as? [String] ?? []).contains("apple") }
    var body: some View {
        StudioNavigation {
            Form {
                Section { Text(StudioStrings.text(enabled ? "Plans renew monthly. Cancel anytime in your store account." : "Billing is being prepared. No charge will be made.")) }
                ForEach(products) { product in
                    Section { Text(product.displayName).font(.headline); Text(product.description); Button(product.displayPrice) { Task { await purchase(product) } }.disabled(busy || !enabled) }
                }
                if enabled {
                    Section { Button(StudioStrings.text("Restore purchases")) { Task { await restore() } }.disabled(busy); Link(StudioStrings.text("Manage subscription"), destination: URL(string: "https://apps.apple.com/account/subscriptions")!) }
                }
                if !message.isEmpty { Section { Text(message).foregroundStyle(.secondary) } }
                if busy { ProgressView() }
                Section { Link("Privacy", destination: URL(string: "https://edit.lazying.art/privacy")!) }
            }.navigationTitle(StudioStrings.text("Plans and billing")).toolbar { ToolbarItem(placement: .cancellationAction) { Button(StudioStrings.text("Close")) { dismiss() } } }
                .task {
                    await load()
                    guard enabled else { return }
                    let context = store.api.contextKey
                    for await result in StoreKit.Transaction.updates {
                        if Task.isCancelled || context != store.api.contextKey { break }
                        do { try await send(result, context: context) } catch { message = error.localizedDescription }
                    }
                }
        }
    }
    private func load() async {
        do {
            catalog = try await store.api.json("/accounts/billing/catalog")
            guard enabled else { products = []; return }
            let ids = (catalog["plans"] as? [[String: Any]] ?? []).compactMap {$0["product"] as? String}
            products = try await Product.products(for: ids).sorted {$0.price < $1.price}
            message = products.isEmpty ? StudioStrings.text("Store products are not available yet.") : ""
        } catch { message = error.localizedDescription }
    }
    private func send(_ result: VerificationResult<StoreKit.Transaction>, context: String) async throws {
        guard context == store.api.contextKey, enabled, case .verified(let transaction) = result else { throw StudioFailure(message: "Purchase could not be verified for this Studio account.", status: 0) }
        var environment = "Production"
        if #available(iOS 16.0, macCatalyst 16.0, *) { environment = transaction.environment == .sandbox ? "Sandbox" : "Production" }
        _ = try await store.api.json("/accounts/billing/verify", method: "POST", body: ["provider": "apple", "signedTransaction": result.jwsRepresentation, "environment": environment])
        guard context == store.api.contextKey else { throw CancellationError() }
        await transaction.finish()
    }
    private func purchase(_ product: Product) async {
        guard enabled, !busy, let raw = catalog["accountToken"] as? String, let token = UUID(uuidString: raw) else { return }
        busy = true; defer { busy = false }
        let context = store.api.contextKey
        do {
            switch try await product.purchase(options: [.appAccountToken(token)]) {
            case .success(let result): try await send(result, context: context); await load()
            case .pending: message = StudioStrings.text("Waiting for payment confirmation")
            case .userCancelled: break
            @unknown default: message = StudioStrings.text("Store request could not finish.")
            }
        } catch { message = error.localizedDescription }
    }
    private func restore() async {
        guard enabled, !busy else { return }; busy = true; defer { busy = false }
        let context = store.api.contextKey
        do { try await AppStore.sync(); for await result in StoreKit.Transaction.currentEntitlements { try await send(result, context: context) }; await load() }
        catch { message = error.localizedDescription }
    }
}

struct StudioPhotoPicker: UIViewControllerRepresentable {
    let completion: (Result<PendingStudioUpload, Error>) -> Void
    let onLoading: () -> Void
    func makeUIViewController(context: Context) -> PHPickerViewController {
        var configuration = PHPickerConfiguration(); configuration.filter = .videos; configuration.selectionLimit = 1
        configuration.preferredAssetRepresentationMode = .current
        let picker = PHPickerViewController(configuration: configuration); picker.delegate = context.coordinator
        return picker
    }
    func updateUIViewController(_ controller: PHPickerViewController, context: Context) {}
    func makeCoordinator() -> Coordinator { Coordinator(self) }
    final class Coordinator: NSObject, PHPickerViewControllerDelegate {
        let parent: StudioPhotoPicker
        init(_ parent: StudioPhotoPicker) { self.parent = parent }
        func picker(_ picker: PHPickerViewController, didFinishPicking results: [PHPickerResult]) {
            guard let provider = results.first?.itemProvider else { picker.dismiss(animated: true); return }
            parent.onLoading()
            let completion = parent.completion
            provider.loadFileRepresentation(forTypeIdentifier: UTType.movie.identifier) { url, error in
                let result: Result<PendingStudioUpload, Error>
                do {
                    guard let url else { throw error ?? StudioFailure(message: "The selected video could not be opened.", status: 0) }
                    result = .success(try StudioFiles.copyVideo(url))
                } catch { result = .failure(error) }
                DispatchQueue.main.async { completion(result) }
            }
        }
    }
}

struct StudioEditorSheet: View {
    @EnvironmentObject private var store: StudioStore
    @Environment(\.dismiss) private var dismiss
    let path: String
    @State private var loading = true
    @State private var failure: String?
    var body: some View {
        StudioNavigation {
            ZStack {
                StudioWebEditor(api: store.api, path: path, loading: $loading, failure: $failure)
                if loading { ProgressView(StudioStrings.text("Opening editor…")).padding(24).background(.regularMaterial, in: RoundedRectangle(cornerRadius: 16)) }
                if let failure { VStack(spacing: 16) { Text(failure); Button(StudioStrings.text("Close")) { dismiss() } }.padding(24).background(.regularMaterial, in: RoundedRectangle(cornerRadius: 16)) }
            }.navigationTitle(StudioStrings.text("Studio editor")).navigationBarTitleDisplayMode(.inline)
                .toolbar { ToolbarItem(placement: .confirmationAction) { Button(StudioStrings.text("Done")) { dismiss() } } }
        }
    }
}

struct StudioWebEditor: UIViewRepresentable {
    let api: StudioAPI
    let path: String
    @Binding var loading: Bool
    @Binding var failure: String?
    func makeUIView(context: Context) -> WKWebView {
        let config = WKWebViewConfiguration(); config.websiteDataStore = .nonPersistent(); config.allowsInlineMediaPlayback = true
        let web = WKWebView(frame: .zero, configuration: config)
        web.navigationDelegate = context.coordinator
        web.allowsBackForwardNavigationGestures = true
        Task { @MainActor in
            do {
                for cookie in api.webCookies { await web.configuration.websiteDataStore.httpCookieStore.setCookie(cookie) }
                var url = URLComponents(url: try api.url(path), resolvingAgainstBaseURL: false)!
                url.queryItems = (url.queryItems ?? []) + [URLQueryItem(name: "interfaceLanguage", value: StudioStrings.language)]
                web.load(URLRequest(url: url.url!))
            } catch { failure = error.localizedDescription; loading = false }
        }
        return web
    }
    func updateUIView(_ web: WKWebView, context: Context) {}
    func makeCoordinator() -> Coordinator { Coordinator(self) }
    final class Coordinator: NSObject, WKNavigationDelegate {
        let parent: StudioWebEditor
        init(_ parent: StudioWebEditor) { self.parent = parent }
        func webView(_ webView: WKWebView, didFinish navigation: WKNavigation!) { parent.loading = false }
        func webView(_ webView: WKWebView, didFail navigation: WKNavigation!, withError error: Error) { parent.failure = error.localizedDescription; parent.loading = false }
        func webView(_ webView: WKWebView, didFailProvisionalNavigation navigation: WKNavigation!, withError error: Error) { parent.failure = error.localizedDescription; parent.loading = false }
        func webView(_ webView: WKWebView, decidePolicyFor action: WKNavigationAction, decisionHandler: @escaping (WKNavigationActionPolicy) -> Void) {
            guard let url = action.request.url else { decisionHandler(.cancel); return }
            if (url.host == parent.api.origin.host && url.scheme == "https" && url.port == parent.api.origin.port && url.user == nil && url.password == nil) || url.scheme == "about" || url.scheme == "blob" { decisionHandler(.allow) }
            else { if action.navigationType == .linkActivated && url.scheme == "https" { UIApplication.shared.open(url) }; decisionHandler(.cancel) }
        }
    }
}

// The same reviewed dictionaries are used by native apps and login desktop.
enum StudioStrings {
    static let languages = [("en", "English"), ("zh-Hans", "简体中文"), ("zh-Hant", "繁體中文"), ("ja", "日本語"), ("ko", "한국어"), ("vi", "Tiếng Việt"), ("ar", "العربية"), ("fr", "Français"), ("es", "Español"), ("de", "Deutsch"), ("ru", "Русский")]
    static let dictionaries: [String: [String: String]] = {
        var tables: [String: [String: String]] = [:]
        for (code, _) in languages {
            if let url = Bundle.main.url(forResource: code, withExtension: "json", subdirectory: "StudioLocales"), let data = try? Data(contentsOf: url), let values = try? JSONDecoder().decode([String: String].self, from: data) { tables[code] = values }
        }
        return tables
    }()
    static var language: String {
        let saved = UserDefaults.standard.string(forKey: "studio.interfaceLanguage") ?? ""
        if languages.contains(where: { $0.0 == saved }) { return saved }
        let preferred = Locale.preferredLanguages.first ?? "en"
        if preferred.hasPrefix("zh") { return preferred.contains("Hant") || preferred.contains("TW") || preferred.contains("HK") ? "zh-Hant" : "zh-Hans" }
        let code = String(preferred.prefix(2)); return languages.contains(where: { $0.0 == code }) ? code : "en"
    }
    static func text(_ value: String) -> String { dictionaries[language]?[value] ?? value }
}

struct StudioLanguagePicker: View {
    @AppStorage("studio.interfaceLanguage") private var language = ""
    var body: some View {
        Picker(StudioStrings.text("Language"), selection: $language) {
            ForEach(StudioStrings.languages, id: \.0) { Text($0.1).tag($0.0) }
        }.onAppear { if language.isEmpty { language = StudioStrings.language } }
    }
}
