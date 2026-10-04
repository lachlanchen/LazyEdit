import SwiftUI
import UniformTypeIdentifiers
import AVKit

struct StudioPublishChoices: Codable, Equatable {
    var burnSubtitles = true
    // Renderer order is deliberately reversed by the server; this list is bottom-to-top.
    var languages = ["zh-Hant", "ja", "en"]
    var lift = 0.0
    var rows = 4
    var fontScale = 1.0
    var fontBold = true
    var outlineBold = true
    var background = "bottom"
    var bottomSpace = 0.4
    var logo = true
    var logoPosition = "top-right"
    var category = ""
    var platforms = ["shipinhao", "instagram", "youtube", "douyin"]
    var context = ""
    var metadataDirection = ""
    var correct = true
    var contextForMetadata = true
    var mode = "new"
    var sessionID = 0

    func object() throws -> [String: Any] {
        try JSONSerialization.jsonObject(with: JSONEncoder().encode(self)) as! [String: Any]
    }
}

struct StudioRun: Identifiable {
    let id: Int
    let title: String
    let ready: Bool
    init?(_ row: [String: Any]) {
        guard let id = row["id"] as? Int else { return nil }
        self.id = id
        title = studioText(row["title"], fallback: "Run \(id)")
        ready = studioText(row["burn_status"]) == "completed"
    }
}

struct StudioSubtitleLanguage: Identifiable {
    let id: String
    let name: String
    init?(_ row: [String: Any]) {
        guard let code = row["code"] as? String, !code.isEmpty else { return nil }
        id = code
        name = studioText(row["name"], fallback: code)
    }
}

struct StudioPendingSubmission: Codable {
    let key: String
    let body: Data
}

@MainActor
final class StudioComposer: ObservableObject {
    @Published var choices = StudioPublishChoices()
    @Published var defaults = StudioPublishChoices()
    @Published var loaded = false
    @Published var publishingEnabled = false
    @Published var busy = false
    @Published var error: String?
    @Published var receipt: String?
    @Published var runs: [StudioRun] = []
    @Published var subtitleLanguages: [StudioSubtitleLanguage] = []
    @Published var geometry: [String: Double] = [:]
    @Published var portrait = false
    @Published var summary: [String] = []
    @Published var preview: String?
    private var planDigest = ""
    @Published var pending: StudioPendingSubmission?
    @Published var canRetrySubmission = false
    private var api: StudioAPI?
    private var workspaceKey = ""
    let videoID: Int
    private var root: String { "/v1/studio/videos/\(videoID)" }
    private var draftURL: URL { StudioFiles.directory.appendingPathComponent(workspaceKey + "-choices-\(videoID).json") }
    private var pendingURL: URL { StudioFiles.directory.appendingPathComponent(workspaceKey + "-submission-\(videoID).json") }

    init(videoID: Int) { self.videoID = videoID }

    func load(api: StudioAPI) async {
        self.api = api
        workspaceKey = api.contextKey
        guard !loaded, !busy else { return }
        busy = true
        defer { busy = false }
        do {
            let result = try await api.json(root + "/composer")
            publishingEnabled = (result["capabilities"] as? [String: Bool])?["publishing"] ?? (api.workspaceMode == "owner")
            defaults = try JSONDecoder().decode(StudioPublishChoices.self, from: JSONSerialization.data(withJSONObject: result["defaults"] ?? [:]))
            choices = defaults
            if let bytes = try? Data(contentsOf: draftURL), let draft = try? JSONDecoder().decode(StudioPublishChoices.self, from: bytes) { choices = draft }
            if !publishingEnabled { choices.platforms = [] }
            if let bytes = try? Data(contentsOf: pendingURL) { pending = try? JSONDecoder().decode(StudioPendingSubmission.self, from: bytes) }
            runs = (result["sessions"] as? [[String: Any]] ?? []).compactMap(StudioRun.init)
            subtitleLanguages = (result["subtitleLanguages"] as? [[String: Any]] ?? []).compactMap(StudioSubtitleLanguage.init)
            if let geometry = result["geometry"] as? [String: Any] { setGeometry(geometry) }
            else { geometry = [:] }
            if portrait { choices.background = "off" }
            loaded = true
            if pending != nil { await reconcile() }
        } catch { self.error = error.localizedDescription }
    }

    private func setGeometry(_ value: [String: Any]?) {
        guard let value else { return }
        portrait = value["portrait"] as? Bool ?? false
        geometry = value.compactMapValues { ($0 as? NSNumber)?.doubleValue }
    }

    func save() {
        guard loaded else { return }
        do { try JSONEncoder().encode(choices).write(to: draftURL, options: [.atomic, .completeFileProtectionUntilFirstUserAuthentication]) }
        catch { self.error = "Your choices could not be saved on this device." }
    }

    func languageName(_ code: String) -> String {
        subtitleLanguages.first { $0.id == code }?.name ?? languageNames[code] ?? code
    }

    func addLanguage(_ code: String) async {
        guard let api, !busy, pending == nil else { return }
        guard choices.languages.count < 8 else { error = "At most eight subtitle rows are available."; return }
        busy = true; error = nil
        defer { busy = false }
        do {
            let result = try await api.json("/api/languages", method: "POST", body: ["languages": [code.trimmingCharacters(in: .whitespacesAndNewlines)]])
            guard let canonical = (result["codes"] as? [String])?.first else { throw StudioFailure(message: "Invalid subtitle language reply", status: 0) }
            if !choices.languages.contains(canonical) {
                choices.languages.append(canonical)
                choices.rows = max(choices.rows, choices.languages.count)
            }
            if let row = (result["languages"] as? [[String: Any]])?.first, let language = StudioSubtitleLanguage(row), !subtitleLanguages.contains(where: { $0.id == canonical }) {
                subtitleLanguages.append(language)
            }
            save()
        } catch { self.error = error.localizedDescription }
    }

    func preset(_ name: String) {
        let context = choices.context, direction = choices.metadataDirection
        choices = defaults
        choices.context = context; choices.metadataDirection = direction
        if name != "defaults" {
            choices.logo = true; choices.logoPosition = "top-right"
            choices.category = name
            choices.burnSubtitles = name != "musia"
            choices.languages = ["zh-Hant", "ja", "en"]
            choices.rows = 4; choices.lift = 0
            choices.background = name == "musia" || portrait ? "off" : "bottom"
        }
    }

    func review() async -> Bool {
        guard let api, !busy, pending == nil else { return false }
        busy = true; error = nil
        defer { busy = false }
        do {
            let result = try await api.json(root + "/plan", method: "POST", body: choices.object())
            summary = result["summary"] as? [String] ?? []
            planDigest = studioText(result["planDigest"])
            preview = result["preview"] as? String
            if let geometry = result["geometry"] as? [String: Any] { setGeometry(geometry) }
            else { geometry = [:] }
            return true
        } catch { self.error = error.localizedDescription; return false }
    }

    func submit(_ action: String) async {
        guard let api, !busy, pending == nil else { return }
        guard action != "publish" || publishingEnabled else { return }
        busy = true; error = nil
        defer { busy = false }
        do {
            let body: [String: Any] = ["action": action, "confirmation": action == "publish" ? "PUBLISH" : "", "form": try choices.object(), "planDigest": planDigest]
            let intent = StudioPendingSubmission(key: UUID().uuidString, body: try JSONSerialization.data(withJSONObject: body))
            // Persist before sending. Never silently generate a second key after a timeout.
            try JSONEncoder().encode(intent).write(to: pendingURL, options: [.atomic, .completeFileProtectionUntilFirstUserAuthentication])
            pending = intent
            let result = try await api.json(root + "/submit", method: "POST", body: body, idempotencyKey: intent.key)
            accept(result)
        } catch {
            self.error = error.localizedDescription
            if (error as? StudioFailure)?.submissionRejected == true { clearPending() }
            else { await reconcile() }
        }
    }

    func reconcile() async {
        guard let api, let pending else { return }
        do {
            let status = try await api.json(root + "/submission?key=\(pending.key)")
            if let result = status["result"] as? [String: Any] { accept(result) }
            else if studioText(status["state"]) == "not_submitted" {
                canRetrySubmission = true
                error = "Studio has no receipt yet. Retry the same request when ready; its saved ID prevents a second task."
            }
            else { error = "Studio received this request but its result is not confirmed. Check Activity or the full editor before submitting again." }
        } catch { self.error = "Could not confirm submission. Check status when the connection returns; no second task has been sent." }
    }

    func retrySubmission() async {
        guard let api, let pending, canRetrySubmission, !busy else { return }
        busy = true; canRetrySubmission = false
        defer { busy = false }
        do {
            let body = try JSONSerialization.jsonObject(with: pending.body) as! [String: Any]
            accept(try await api.json(root + "/submit", method: "POST", body: body, idempotencyKey: pending.key))
        } catch {
            self.error = error.localizedDescription
            if (error as? StudioFailure)?.submissionRejected == true { clearPending() }
            else { await reconcile() }
        }
    }

    private func accept(_ result: [String: Any]) {
        let job = result["job_id"] as? Int
        let session = result["publication_session_id"] as? Int
        receipt = job.map { "Queued as task #\($0). Follow progress in Activity." } ?? "Preparation started. Open the full editor to review subtitles, metadata and the rendered video."
        if let session { choices.sessionID = session }
        clearPending(); save(); error = nil
    }
    private func clearPending() { pending = nil; canRetrySubmission = false; try? FileManager.default.removeItem(at: pendingURL) }

    func importContext(_ url: URL) {
        let access = url.startAccessingSecurityScopedResource()
        defer { if access { url.stopAccessingSecurityScopedResource() } }
        do {
            let size = try url.resourceValues(forKeys: [.fileSizeKey]).fileSize ?? 0
            guard size < 100_000 else { throw StudioFailure(message: "Choose a text or Markdown note smaller than 100 KB.", status: 0) }
            let text = try String(contentsOf: url, encoding: .utf8)
            guard text.count <= 16000 else { throw StudioFailure(message: "Keep the context under 16,000 characters.", status: 0) }
            choices.context = text
        } catch { self.error = error.localizedDescription }
    }
}

private let languageNames = ["en": "English", "ja": "Japanese", "zh-Hant": "Chinese · Traditional", "zh-Hans": "Chinese · Simplified", "fr": "French"]
private let platformNames = [("shipinhao", "Shipinhao"), ("instagram", "Instagram"), ("youtube", "YouTube"), ("douyin", "Douyin"), ("xiaohongshu", "Xiaohongshu"), ("bilibili", "Bilibili")]

struct StudioComposerView: View {
    @EnvironmentObject private var store: StudioStore
    @Environment(\.dismiss) private var dismiss
    let video: StudioVideo
    @StateObject private var model: StudioComposer
    @State private var importNote = false
    @State private var review = false
    @State private var editor = false
    @State private var showLanguages = false
    @State private var languageQuery = ""
    @State private var advanced = false
    @State private var reviewPlayer: AVPlayer?

    init(video: StudioVideo) { self.video = video; _model = StateObject(wrappedValue: StudioComposer(videoID: video.id)) }

    var body: some View {
        StudioNavigation {
            Form {
                if let error = model.error { Section { Text(error).foregroundStyle(.orange); if !model.loaded { Button(StudioStrings.text("Try again")) { Task { await model.load(api: store.api) } } } } }
                if !model.loaded { ProgressView(StudioStrings.text("Loading your Studio defaults…")) }
                else {
                    Section {
                        Text(video.title).font(.headline)
                        if let receipt = model.receipt { Label(receipt, systemImage: "checkmark.circle").foregroundStyle(.green) }
                        if model.pending != nil { Button(StudioStrings.text("Check submission status")) { Task { await model.reconcile() } } }
                        if model.canRetrySubmission { Button(StudioStrings.text("Retry same submission")) { Task { await model.retrySubmission() } }.disabled(model.busy) }
                        Picker(StudioStrings.text("Output"), selection: $model.choices.mode) {
                            Text(StudioStrings.text("Prepare a new run")).tag("new")
                            Text(StudioStrings.text("Reuse a finished run")).tag("reuse")
                        }.accessibilityIdentifier("studio.runMode")
                        if model.choices.mode == "reuse" {
                            Picker(StudioStrings.text("Finished run"), selection: $model.choices.sessionID) {
                                Text(StudioStrings.text("Current output")).tag(0)
                                ForEach(model.runs.filter(\.ready)) { Text($0.title).tag($0.id) }
                            }
                            Text(StudioStrings.text("Reuse keeps its subtitles, logo, cover and metadata. Choose only platforms that still need this version.")).font(.footnote).foregroundStyle(.secondary)
                        } else {
                            Menu("Start from a preset") {
                                Button(StudioStrings.text("Current website defaults")) { model.preset("defaults") }
                                Button(StudioStrings.text("Daily recording · EN / JP / ZH")) { model.preset("simplelife") }
                                Button(StudioStrings.text("LALACHAN story · EN / JP / ZH")) { model.preset("lalachan") }
                                Button(StudioStrings.text("Musia recording · no subtitles")) { model.preset("musia") }
                            }
                        }
                    } footer: { Text(StudioStrings.text("Choices are saved for this video on this device. Website defaults stay unchanged.")) }
                    if model.choices.mode == "new" {
                        contextSection
                        subtitlesSection
                        appearanceSection
                    }
                    if model.publishingEnabled { Section(StudioStrings.text("Publish to")) {
                        ForEach(platformNames, id: \.0) { key, name in
                            Toggle(name, isOn: Binding(get: { model.choices.platforms.contains(key) }, set: { enabled in
                                model.choices.platforms.removeAll { $0 == key }; if enabled { model.choices.platforms.append(key) }
                            }))
                        }
                    } }
                    Section {
                        Button {
                            UIApplication.shared.sendAction(#selector(UIResponder.resignFirstResponder), to: nil, from: nil, for: nil)
                            Task { if await model.review() { review = true } }
                        } label: {
                            HStack { if model.busy { ProgressView() }; Label(StudioStrings.text("Review & continue"), systemImage: "checkmark.circle") }
                        }.disabled(model.busy || model.pending != nil).accessibilityIdentifier("studio.reviewChoices")
                        Button(StudioStrings.text("Full editor · subtitles, metadata & cover")) { editor = true }
                            .accessibilityIdentifier("studio.composerEditor")
                    } footer: { Text(StudioStrings.text(model.publishingEnabled ? "Preparation and publication use the existing Studio pipeline. You can prepare without posting, or queue preparation and publication together." : "Process your video, then preview the edited result. Social accounts are optional.")) }
                }
            }.accessibilityIdentifier("studio.composerForm").studioKeyboardDismissal()
                .navigationTitle(StudioStrings.text(model.publishingEnabled ? "Prepare & publish" : "Edit & preview")).navigationBarTitleDisplayMode(.inline)
                .toolbar {
                    ToolbarItem(placement: .confirmationAction) { Button(StudioStrings.text("Done")) { dismiss() } }
                    ToolbarItemGroup(placement: .keyboard) { Spacer(); Button(StudioStrings.text("Hide keyboard")) { UIApplication.shared.sendAction(#selector(UIResponder.resignFirstResponder), to: nil, from: nil, for: nil) } }
                }
                .task { await model.load(api: store.api) }
                .onChange(of: model.choices) { _ in model.save() }
                .sheet(isPresented: $review, onDismiss: { reviewPlayer?.pause(); reviewPlayer = nil }) { reviewSheet }
                .sheet(isPresented: $showLanguages) { languageSheet }
                .sheet(isPresented: $editor) { StudioEditorSheet(path: "/editor?videoId=\(video.id)") }
                .fileImporter(isPresented: $importNote, allowedContentTypes: [.plainText, .text], allowsMultipleSelection: false) { result in
                    do { if let url = try result.get().first { model.importContext(url) } } catch { model.error = error.localizedDescription }
                }
        }
    }

    private var contextSection: some View {
        Section {
            TextEditor(text: $model.choices.context).frame(minHeight: 110).accessibilityIdentifier("studio.context")
            Button { importNote = true } label: { Label(StudioStrings.text("Import a script or context note"), systemImage: "doc.text") }
            Toggle(StudioStrings.text("Correct recognition errors"), isOn: $model.choices.correct)
            Toggle(StudioStrings.text("Use context for metadata"), isOn: $model.choices.contextForMetadata)
            DisclosureGroup("Metadata direction") {
                StudioContextInput(text: $model.choices.metadataDirection)
                Picker(StudioStrings.text("Category"), selection: $model.choices.category) {
                    Text(StudioStrings.text("Let Studio decide")).tag(""); Text(StudioStrings.text("SimpleLife")).tag("simplelife")
                    Text(StudioStrings.text("LALACHAN")).tag("lalachan"); Text(StudioStrings.text("Musia")).tag("musia")
                    Text(StudioStrings.text("LalaMV")).tag("lalamv"); Text(StudioStrings.text("LazyingArt")).tag("lazyingart")
                }
            }
        } header: { Text(StudioStrings.text("What is this video about?")) }
        footer: { Text(StudioStrings.text("Add names, background or the original script. Studio checks the full conversation, fixes plausible ASR mistakes and keeps the actual timing. The script is a reference, not a replacement transcript. Metadata describes the video, not the production process.")) }
    }

    private var subtitlesSection: some View {
        Section {
            Toggle(StudioStrings.text("Burn subtitles"), isOn: $model.choices.burnSubtitles)
            if model.choices.burnSubtitles {
                Button { showLanguages = true } label: {
                    VStack(alignment: .leading, spacing: 6) {
                        Text(StudioStrings.text("Languages & order"))
                        Text(StudioStrings.text("Top → bottom: ") + model.choices.languages.reversed().map { model.languageName($0) }.joined(separator: " · ")).font(.caption).foregroundStyle(.secondary)
                    }
                }
                DisclosureGroup("Subtitle appearance", isExpanded: $advanced) {
                    Stepper("Reserved rows: \(model.choices.rows)", value: $model.choices.rows, in: max(1, model.choices.languages.count)...8)
                    StudioLabeledValue("Lift", value: String(format: "%.0f%%", model.choices.lift * 100))
                    Slider(value: $model.choices.lift, in: 0...0.4, step: 0.01)
                    Button(StudioStrings.text("No lift")) { model.choices.lift = 0 }
                    StudioLabeledValue(StudioStrings.text("Font size"), value: String(format: "%.2f×", model.choices.fontScale))
                    Slider(value: $model.choices.fontScale, in: 0.6...2.5, step: 0.05)
                    Toggle(StudioStrings.text("Bold text"), isOn: $model.choices.fontBold)
                    Toggle(StudioStrings.text("Thick outline"), isOn: $model.choices.outlineBold)
                }
            }
        } header: { Text(StudioStrings.text("Subtitles")) }
        footer: { Text(model.choices.burnSubtitles ? "Uses corrected subtitles, grammar colours, Japanese furigana and kana readings, and Chinese pinyin. Reserved rows keep font sizes consistent when fewer languages are selected." : "Your video can keep its existing on-screen text. Logo and metadata are prepared independently.") }
    }

    private var appearanceSection: some View {
        Section {
            Picker(StudioStrings.text("Background fill"), selection: $model.choices.background) {
                Text(StudioStrings.text("Off · original frame")).tag("off")
                if !model.portrait { Text(StudioStrings.text("Portrait · bottom space")).tag("bottom"); Text(StudioStrings.text("Portrait · centred")).tag("center") }
            }.disabled(model.portrait)
            if model.portrait { Text(StudioStrings.text("Portrait source: background fill is disabled.")).font(.footnote).foregroundStyle(.secondary) }
            if model.choices.background == "bottom" && !model.portrait {
                StudioLabeledValue(StudioStrings.text("Bottom space"), value: String(format: "%.0f%%", model.choices.bottomSpace * 100))
                Slider(value: $model.choices.bottomSpace, in: 0...0.8, step: 0.01)
                Text(StudioStrings.text("The original frame fits above this space without cropping. The review shows the resulting layout.")).font(.footnote).foregroundStyle(.secondary)
            }
            Toggle(StudioStrings.text("Studio logo"), isOn: $model.choices.logo)
            if model.choices.logo {
                Picker(StudioStrings.text("Logo position"), selection: $model.choices.logoPosition) {
                    Text(StudioStrings.text("Top right")).tag("top-right"); Text(StudioStrings.text("Top left")).tag("top-left")
                    Text(StudioStrings.text("Bottom right")).tag("bottom-right"); Text(StudioStrings.text("Bottom left")).tag("bottom-left")
                }
            }
        } header: { Text(StudioStrings.text("Frame & logo")) }
    }

    private var languageSheet: some View {
        StudioNavigation {
            List {
                Section {
                    ForEach(model.choices.languages, id: \.self) { lang in
                        HStack { Text(model.languageName(lang)); Spacer(); Text(model.choices.languages.first == lang ? "Bottom" : model.choices.languages.last == lang ? "Top" : "").font(.caption).foregroundStyle(.secondary) }
                    }
                    .onMove { from, to in model.choices.languages.move(fromOffsets: from, toOffset: to) }
                    .onDelete { model.choices.languages.remove(atOffsets: $0) }
                } header: { Text(StudioStrings.text("Bottom → top")) } footer: { Text(StudioStrings.text("Drag to reorder. The first language is closest to the bottom of the video.")) }
                Section(StudioStrings.text("Add a language")) {
                    TextField("Search or enter a language code", text: $languageQuery).textInputAutocapitalization(.never).autocorrectionDisabled()
                    if !languageQuery.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty {
                        Button("Use this language code") { Task { await model.addLanguage(languageQuery) } }.disabled(model.busy)
                    }
                    if let error = model.error { Text(error).foregroundStyle(.red) }
                    ForEach(model.subtitleLanguages.filter { !model.choices.languages.contains($0.id) && (languageQuery.isEmpty || ($0.name + " " + $0.id).localizedCaseInsensitiveContains(languageQuery)) }) { language in
                        Button(language.name + " · " + language.id) { Task { await model.addLanguage(language.id) } }.disabled(model.busy)
                    }
                    Button(StudioStrings.text("EN / JP / ZH / FR · top to bottom")) { model.choices.languages = ["fr", "zh-Hant", "ja", "en"]; model.choices.rows = max(4, model.choices.rows) }
                }
            }.environment(\.editMode, .constant(.active))
                .navigationTitle(StudioStrings.text("Subtitle order")).navigationBarTitleDisplayMode(.inline)
                .toolbar { ToolbarItem(placement: .confirmationAction) { Button(StudioStrings.text("Done")) { showLanguages = false } } }
        }
    }

    private var reviewSheet: some View {
        StudioNavigation {
            List {
                Section { Text(video.title).font(.headline); ForEach(model.summary, id: \.self) { Text($0) } }
                if let path = model.preview {
                    Section(StudioStrings.text("Finished output")) {
                        if let reviewPlayer { VideoPlayer(player: reviewPlayer).frame(height: 280) }
                        else { Button(StudioStrings.text("Preview this run")) {
                            do {
                                let asset = AVURLAsset(url: try store.api.url(path), options: [AVURLAssetHTTPCookiesKey: store.api.webCookie.map { [$0] } ?? []])
                                reviewPlayer = AVPlayer(playerItem: AVPlayerItem(asset: asset))
                            } catch { model.error = error.localizedDescription }
                        } }
                    }
                }
                if model.geometry["fill"] == 1 { Section(StudioStrings.text("Frame layout")) { StudioLayoutPreview(geometry: model.geometry) } }
                if model.publishingEnabled { Section(StudioStrings.text("Platforms")) { Text(model.choices.platforms.map { key in platformNames.first { $0.0 == key }?.1 ?? key }.joined(separator: ", ")) } }
                if let error = model.error { Text(error).foregroundStyle(.orange) }
                if let receipt = model.receipt { Text(receipt).foregroundStyle(.green) }
                Section {
                    if model.pending != nil { Button(StudioStrings.text("Check submission status")) { Task { await model.reconcile() } } }
                    else {
                        if model.choices.mode == "new" {
                            Button(StudioStrings.text("Prepare only · do not post")) { Task { await model.submit("prepare") } }.disabled(model.busy || model.receipt != nil).accessibilityIdentifier("studio.prepareOnly")
                        }
                        if model.publishingEnabled { Button(model.choices.mode == "reuse" ? "Queue this run for publication" : "Prepare & queue publication") { Task { await model.submit("publish") } }
                            .disabled(model.busy || model.choices.platforms.isEmpty || model.receipt != nil).accessibilityIdentifier("studio.confirmPublish")
                        }
                    }
                    if model.busy { ProgressView(StudioStrings.text("Submitting once…")) }
                    if model.canRetrySubmission { Button(StudioStrings.text("Retry same submission")) { Task { await model.retrySubmission() } }.disabled(model.busy) }
                    Button(StudioStrings.text("Open full editor")) { review = false; editor = true }
                } footer: { Text(StudioStrings.text(model.publishingEnabled ? "Publication sends this video to the selected accounts. Studio continues the task after you close the app. Check Activity for progress and any login request." : "Process your video, then preview the edited result. Social accounts are optional.")) }
            }.navigationTitle(StudioStrings.text("Review choices")).navigationBarTitleDisplayMode(.inline)
                .toolbar { ToolbarItem(placement: .confirmationAction) { Button(StudioStrings.text("Done")) { review = false } } }
        }
    }
}

struct StudioLayoutPreview: View {
    let geometry: [String: Double]
    var body: some View {
        let width = geometry["outputWidth"] ?? 1080, height = geometry["outputHeight"] ?? 1920
        let fgWidth = geometry["foregroundWidth"] ?? width, fgHeight = geometry["foregroundHeight"] ?? 600
        let top = geometry["top"] ?? 0, bottom = geometry["bottom"] ?? 0
        VStack(spacing: 12) {
            ZStack(alignment: .topLeading) {
                RoundedRectangle(cornerRadius: 12).fill(Color.teal.opacity(0.15))
                Rectangle().fill(Color.teal.opacity(0.6)).frame(width: 170 * fgWidth / width, height: 170 * fgHeight / width)
                    .overlay(Text(StudioStrings.text("Original video")).font(.caption).foregroundStyle(.white))
                    .offset(x: 85 * (1 - fgWidth / width), y: 170 * top / width)
            }.frame(width: 170, height: 170 * height / width).clipped()
            Text("Top \(Int((top / height * 100).rounded()))% · Video \(Int((fgHeight / height * 100).rounded()))% · Bottom \(Int((bottom / height * 100).rounded()))%").font(.caption)
            Text(StudioStrings.text("Layout preview; the final render includes your chosen subtitles and logo.")).font(.caption).foregroundStyle(.secondary)
        }.frame(maxWidth: .infinity).padding(.vertical)
    }
}

struct StudioRemovedVideos: View {
    @EnvironmentObject private var store: StudioStore
    @Environment(\.dismiss) private var dismiss
    var body: some View {
        StudioNavigation {
            List {
                Section { Text(StudioStrings.text("Removed videos keep their files, runs and publication history. Restore them whenever you need them.")).font(.footnote).foregroundStyle(.secondary) }
                StudioErrorBanner()
                ForEach(store.hiddenVideos) { video in
                    HStack {
                        Text(video.title).lineLimit(2)
                        Spacer()
                        Button(StudioStrings.text("Restore")) { Task { await store.setHidden(video, hidden: false) } }.disabled(store.changingVisibility.contains(video.id))
                    }
                }
                if store.hiddenVideos.isEmpty { Text(StudioStrings.text("No removed videos")).foregroundStyle(.secondary) }
            }.navigationTitle(StudioStrings.text("Removed videos")).navigationBarTitleDisplayMode(.inline)
                .toolbar { ToolbarItem(placement: .confirmationAction) { Button(StudioStrings.text("Done")) { dismiss() } } }
                .task { await store.refreshHidden() }.refreshable { await store.refreshHidden() }
        }
    }
}

struct StudioJobSheet: View {
    @EnvironmentObject private var store: StudioStore
    @Environment(\.dismiss) private var dismiss
    let job: StudioJob
    @State private var image: UIImage?
    @State private var error: String?
    @State private var editor = false
    var body: some View {
        StudioNavigation {
            List {
                Text(job.title).font(.headline)
                StudioLabeledValue("Status", value: job.status.capitalized)
                Text(job.platforms)
                if !job.detail.isEmpty { Text(job.detail) }
                if let message = job.attentionMessage {
                    Text(message).foregroundStyle(.orange)
                    if let image { Image(uiImage: image).resizable().scaledToFit().padding().background(.white) }
                    else if job.attentionURL != nil && error == nil { ProgressView(StudioStrings.text("Loading verification image…")) }
                    if let error { Text(error).foregroundStyle(.orange) }
                    Text(StudioStrings.text("Finish verification, then return to Activity. The publisher keeps waiting; do not submit another post.")).font(.footnote)
                }
                if job.videoID != nil { Button(StudioStrings.text("Open this video in Studio")) { editor = true } }
            }.navigationTitle(StudioStrings.text("Publication task")).navigationBarTitleDisplayMode(.inline)
                .toolbar { ToolbarItem(placement: .confirmationAction) { Button(StudioStrings.text("Done")) { dismiss() } } }
                .sheet(isPresented: $editor) { StudioEditorSheet(path: "/editor?videoId=\(job.videoID ?? 0)") }
                .task {
                    if let path = job.attentionURL {
                        do { image = UIImage(data: try await store.api.data(path)); if image == nil { error = "The verification image is unavailable. Refresh Activity for the current request." } }
                        catch { self.error = error.localizedDescription }
                    }
                }
        }
    }
}
