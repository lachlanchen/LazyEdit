import SwiftUI
import AVKit
import PhotosUI
import UniformTypeIdentifiers
import WebKit

private let studioTint = Color(red: 0.13, green: 0.37, blue: 0.29)

struct NativeStudioRoot: View {
    @StateObject private var store = StudioStore()
    @State private var tab = 0
    var body: some View {
        Group {
            if store.signedIn {
                TabView(selection: $tab) {
                    StudioLibraryView(onUpload: { tab = 1 }).tabItem { Label("Studio", systemImage: "square.stack") }.tag(0)
                    StudioUploadView().tabItem { Label("Upload", systemImage: "plus.circle") }.tag(1)
                    StudioJobsView().tabItem { Label("Activity", systemImage: "clock.arrow.circlepath") }.tag(2)
                    StudioAccountView().tabItem { Label("Account", systemImage: "person.crop.circle") }.tag(3)
                }
            } else { StudioLoginView() }
        }
        .tint(studioTint)
        .environmentObject(store)
    }
}

struct StudioLoginView: View {
    @EnvironmentObject private var store: StudioStore
    @State private var password = ""
    var body: some View {
        NavigationStack {
            ScrollView {
                VStack(alignment: .leading, spacing: 24) {
                    Image("StudioMark").resizable().frame(width: 76, height: 76).clipShape(RoundedRectangle(cornerRadius: 19))
                    VStack(alignment: .leading, spacing: 8) {
                        Text("Your stories.\nYour Studio.").font(.system(size: 38, weight: .bold, design: .rounded))
                        Text("A quiet space to edit, prepare and share your videos.").foregroundStyle(.secondary)
                    }
                    VStack(spacing: 16) {
                        TextField("Username", text: $store.username).textContentType(.username).textInputAutocapitalization(.never).autocorrectionDisabled().accessibilityIdentifier("studio.username")
                        SecureField("Password", text: $password).textContentType(.password).submitLabel(.go).accessibilityIdentifier("studio.password")
                            .onSubmit { signIn() }
                    }.textFieldStyle(.roundedBorder)
                    StudioErrorBanner()
                    Button(action: signIn) {
                        HStack { Spacer(); if store.signingIn { ProgressView().tint(.white) }; Text(store.signingIn ? "Signing in…" : "Sign in").bold(); Spacer() }.padding(.vertical, 7)
                    }.buttonStyle(.borderedProminent).disabled(store.signingIn || password.isEmpty || store.username.isEmpty).accessibilityIdentifier("studio.signIn")
                    Text("edit.lazying.art").font(.footnote).foregroundStyle(.secondary)
                }.padding(28).padding(.top, 48)
            }.background(Color(uiColor: .systemGroupedBackground))
        }
    }
    private func signIn() {
        guard !store.signingIn, !password.isEmpty else { return }
        UIApplication.shared.sendAction(#selector(UIResponder.resignFirstResponder), to: nil, from: nil, for: nil)
        let value = password
        Task { await store.login(password: value); if store.signedIn { password = "" } }
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
    private var filtered: [StudioVideo] { search.isEmpty ? store.videos : store.videos.filter { $0.title.localizedCaseInsensitiveContains(search) } }
    var body: some View {
        NavigationStack {
            List {
                if store.error != nil { StudioErrorBanner().listRowSeparator(.hidden) }
                if store.loadingVideos && store.videos.isEmpty { ProgressView("Opening your library…") }
                if !store.loadingVideos && store.videos.isEmpty {
                    VStack(spacing: 14) {
                        Image(systemName: "film.stack").font(.largeTitle)
                        Text("Your next story starts here").font(.headline)
                        Text("Choose a video from Photos or Files to add it to your Studio.").foregroundStyle(.secondary).multilineTextAlignment(.center)
                        Button("Add a video", action: onUpload).buttonStyle(.borderedProminent)
                    }.padding(.vertical, 32).frame(maxWidth: .infinity)
                }
                ForEach(filtered) { video in
                    NavigationLink(value: video) {
                        HStack(spacing: 14) {
                            StudioThumbnail(video: video)
                            VStack(alignment: .leading, spacing: 7) {
                                Text(video.title).font(.headline).lineLimit(2)
                                Text(video.created).font(.caption).foregroundStyle(.secondary)
                            }
                        }.padding(.vertical, 5)
                    }
                }
            }
            .navigationTitle("Your Studio")
            .searchable(text: $search, prompt: "Find a video")
            .toolbar { ToolbarItem(placement: .navigationBarTrailing) { Button(action: onUpload) { Image(systemName: "plus") }.accessibilityLabel("Add video") } }
            .navigationDestination(for: StudioVideo.self) { StudioVideoView(video: $0) }
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
        NavigationStack {
            ScrollView {
                VStack(alignment: .leading, spacing: 24) {
                    Text("Bring your next story.").font(.title2.bold())
                    Text("Your original video stays on your device. Studio prepares a separate copy for editing and publication.").foregroundStyle(.secondary)
                    HStack(spacing: 14) {
                        Button { photos = true } label: { Label("Photos", systemImage: "photo.on.rectangle").frame(maxWidth: .infinity).padding(.vertical, 12) }
                        Button { files = true } label: { Label("Files", systemImage: "folder").frame(maxWidth: .infinity).padding(.vertical, 12) }
                    }.buttonStyle(.bordered).disabled(store.pending != nil || store.preparingFile || store.uploading)
                    if store.preparingFile { ProgressView("Preparing your video…") }
                    StudioErrorBanner()
                    if let pending = store.pending {
                        VStack(alignment: .leading, spacing: 14) {
                            Label(pending.filename, systemImage: "video").font(.headline).lineLimit(2)
                            Text(ByteCountFormatter.string(fromByteCount: pending.size, countStyle: .file)).foregroundStyle(.secondary)
                            ProgressView(value: store.uploadProgress)
                            Text(store.uploadMessage).font(.subheadline).foregroundStyle(.secondary)
                            if store.uploading { Button("Pause upload") { store.pauseUpload() }.buttonStyle(.bordered) }
                            else {
                                HStack {
                                    Button(pending.uploadID == nil ? "Upload video" : "Resume upload") { store.beginUpload() }.buttonStyle(.borderedProminent).accessibilityIdentifier("studio.upload")
                                    Spacer()
                                    Button("Remove", role: .destructive) { remove = true }
                                }
                            }
                        }.padding(20).background(Color(uiColor: .secondarySystemGroupedBackground), in: RoundedRectangle(cornerRadius: 18))
                    }
                    if let video = store.uploadedVideo {
                        Label("Added to your Studio", systemImage: "checkmark.circle.fill").foregroundStyle(studioTint)
                        NavigationLink("Open video", value: video).buttonStyle(.borderedProminent)
                    }
                    Text("Uploads can resume after interruptions. Keep the app open for the fastest transfer.").font(.footnote).foregroundStyle(.secondary)
                }.padding(24)
            }.background(Color(uiColor: .systemGroupedBackground))
                .navigationTitle("Upload")
                .navigationDestination(for: StudioVideo.self) { StudioVideoView(video: $0) }
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
                .confirmationDialog("Remove this local upload copy?", isPresented: $remove) {
                    Button("Remove upload copy", role: .destructive) { store.discardUpload() }
                } message: { Text("Your original video stays in Photos or Files. Any unfinished server upload expires automatically.") }
        }
    }
}

struct StudioVideoView: View {
    @EnvironmentObject private var store: StudioStore
    @Environment(\.scenePhase) private var scenePhase
    let video: StudioVideo
    @State private var player: AVPlayer?
    @State private var editor = false
    @State private var steps: [(String, String)] = []
    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 22) {
                if let player { VideoPlayer(player: player).frame(height: 280).clipShape(RoundedRectangle(cornerRadius: 16)) }
                else {
                    Button(action: preview) {
                        VStack(spacing: 12) { Image(systemName: "play.circle.fill").font(.system(size: 48)); Text("Preview video") }.frame(maxWidth: .infinity).frame(height: 200)
                    }.background(studioTint.opacity(0.08), in: RoundedRectangle(cornerRadius: 16))
                }
                Text(video.title).font(.title2.bold())
                Text(video.created).foregroundStyle(.secondary).font(.subheadline)
                StudioErrorBanner()
                Button { player?.pause(); editor = true } label: { Label("Edit & publish", systemImage: "slider.horizontal.3").frame(maxWidth: .infinity).padding(.vertical, 8) }.buttonStyle(.borderedProminent)
                Text("Review subtitles, metadata, logo and target platforms in the full Studio editor before publishing.").font(.footnote).foregroundStyle(.secondary)
                if !steps.isEmpty {
                    Text("Processing").font(.headline)
                    ForEach(steps, id: \.0) { item in HStack { Text(item.0); Spacer(); Text(item.1.capitalized).foregroundStyle(.secondary) }.font(.subheadline) }
                }
            }.padding(24)
        }.navigationTitle("Video").navigationBarTitleDisplayMode(.inline)
            .task { await loadStatus() }
            .refreshable { await loadStatus() }
            .onDisappear { player?.pause() }
            .onChange(of: scenePhase) { phase in if phase != .active { player?.pause() } }
            .sheet(isPresented: $editor) { StudioEditorSheet(path: "/editor?videoId=\(video.id)") }
    }
    private func preview() {
        guard let media = video.media else { return }
        do {
            let asset = AVURLAsset(url: try store.api.url(media), options: [AVURLAssetHTTPCookiesKey: store.api.webCookie.map { [$0] } ?? []])
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
    var body: some View {
        NavigationStack {
            List {
                StudioErrorBanner()
                if store.jobs.isEmpty { Label("No publication tasks to show", systemImage: "checkmark.circle").foregroundStyle(.secondary) }
                ForEach(store.jobs) { job in
                    VStack(alignment: .leading, spacing: 8) {
                        Text(job.title).font(.headline)
                        Label(job.status.capitalized, systemImage: job.status == "done" ? "checkmark.circle.fill" : "clock").foregroundStyle(job.status == "done" ? studioTint : Color.secondary)
                        Text(job.platforms).font(.caption).foregroundStyle(.secondary)
                        if !job.detail.isEmpty { Text(job.detail).font(.subheadline).foregroundStyle(.secondary) }
                    }.padding(.vertical, 8)
                }
            }.navigationTitle("Activity")
                .refreshable { await store.refreshJobs() }
                .task(id: scenePhase) {
                    guard scenePhase == .active else { return }
                    while !Task.isCancelled { await store.refreshJobs(); do { try await Task.sleep(nanoseconds: 15_000_000_000) } catch { break } }
                }
        }
    }
}

struct StudioAccountView: View {
    @EnvironmentObject private var store: StudioStore
    @State private var signOut = false
    @State private var editor = false
    var body: some View {
        NavigationStack {
            Form {
                Section {
                    HStack(spacing: 14) {
                        Image("StudioMark").resizable().frame(width: 52, height: 52).clipShape(RoundedRectangle(cornerRadius: 13))
                        VStack(alignment: .leading, spacing: 4) { Text(store.username).font(.headline); Text("edit.lazying.art").font(.subheadline).foregroundStyle(.secondary) }
                    }.padding(.vertical, 8)
                }
                Section { Button("Open full Studio") { editor = true }; Link("Privacy", destination: URL(string: "https://edit.lazying.art/privacy")!) }
                Section { StudioErrorBanner(); Button("Sign out", role: .destructive) { signOut = true } }
                Section { Text("LazyEdit Studio · \(Bundle.main.object(forInfoDictionaryKey: "CFBundleShortVersionString") as? String ?? "1.0") (\(Bundle.main.object(forInfoDictionaryKey: "CFBundleVersion") as? String ?? ""))").foregroundStyle(.secondary) }
            }.navigationTitle("Account")
                .sheet(isPresented: $editor) { StudioEditorSheet(path: "/home") }
                .confirmationDialog("Sign out of Studio?", isPresented: $signOut) { Button("Sign out", role: .destructive) { Task { await store.logout() } } }
        }
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
        NavigationStack {
            ZStack {
                StudioWebEditor(api: store.api, path: path, loading: $loading, failure: $failure)
                if loading { ProgressView("Opening editor…").padding(24).background(.regularMaterial, in: RoundedRectangle(cornerRadius: 16)) }
                if let failure { VStack(spacing: 16) { Text(failure); Button("Close") { dismiss() } }.padding(24).background(.regularMaterial, in: RoundedRectangle(cornerRadius: 16)) }
            }.navigationTitle("Studio editor").navigationBarTitleDisplayMode(.inline)
                .toolbar { ToolbarItem(placement: .confirmationAction) { Button("Done") { dismiss() } } }
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
                if let cookie = api.webCookie { await web.configuration.websiteDataStore.httpCookieStore.setCookie(cookie) }
                web.load(URLRequest(url: try api.url(path)))
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
