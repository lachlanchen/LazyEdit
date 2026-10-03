import Foundation
import Security
import AuthenticationServices
import CryptoKit
import UIKit

struct StudioFailure: LocalizedError {
    let message: String
    let status: Int
    var submissionRejected: Bool = false
    var errorDescription: String? { message }
}

func studioText(_ value: Any?, fallback: String = "") -> String {
    if let value = value as? String, !value.isEmpty { return value }
    if let value = value as? [String: Any] {
        if let message = value["message"] as? String { return message }
        if let code = value["code"] as? String {
            if code == "too_many_requests" { return "Studio is busy. Please try again shortly." }
            return code.replacingOccurrences(of: "_", with: " ")
        }
    }
    return fallback
}

enum StudioKeychain {
    private static let query: [String: Any] = [
        kSecClass as String: kSecClassGenericPassword,
        kSecAttrService as String: "art.lazying.lazyedit.session",
        kSecAttrAccount as String: "owner",
    ]
    static func read() -> Data? {
        var q = query
        q[kSecReturnData as String] = true
        q[kSecMatchLimit as String] = kSecMatchLimitOne
        var value: CFTypeRef?
        return SecItemCopyMatching(q as CFDictionary, &value) == errSecSuccess ? value as? Data : nil
    }
    static func save(_ data: Data) throws {
        let update = SecItemUpdate(query as CFDictionary, [kSecValueData as String: data] as CFDictionary)
        if update == errSecSuccess { return }
        guard update == errSecItemNotFound else { throw StudioFailure(message: "Could not save the secure session (\(update)).", status: 0) }
        var q = query
        q[kSecValueData as String] = data
        q[kSecAttrAccessible as String] = kSecAttrAccessibleAfterFirstUnlockThisDeviceOnly
        let added = SecItemAdd(q as CFDictionary, nil)
        guard added == errSecSuccess else {
            throw StudioFailure(message: "Could not save the secure session (\(added)).", status: 0)
        }
    }
    static func clear() { SecItemDelete(query as CFDictionary) }
}

struct StudioSession: Codable {
    let cookie: String
    let expires: Date
    let username: String
    var hostedCookie: String? = nil
    var mode: String? = nil
}

class StudioNetworkDelegate: NSObject, URLSessionTaskDelegate {
    // No API endpoint needs a redirect. Never forward a session or replay a
    // mutation to a redirect target, even if a proxy is misconfigured.
    func urlSession(_ session: URLSession, task: URLSessionTask,
                    willPerformHTTPRedirection response: HTTPURLResponse,
                    newRequest request: URLRequest,
                    completionHandler: @escaping (URLRequest?) -> Void) {
        completionHandler(nil)
    }
}

final class StudioUploadProgress: StudioNetworkDelegate {
    let report: (Int64) -> Void
    init(report: @escaping (Int64) -> Void) { self.report = report }
    func urlSession(_ session: URLSession, task: URLSessionTask, didSendBodyData bytesSent: Int64,
                    totalBytesSent: Int64, totalBytesExpectedToSend: Int64) { report(totalBytesSent) }
}

@MainActor
final class StudioAPI {
    let origin = URL(string: "https://edit.lazying.art")!
    private(set) var identity: StudioSession?
    private let session: URLSession
    private var activeReads = 0
    private var waiters: [CheckedContinuation<Void, Never>] = []

    init() {
        let config = URLSessionConfiguration.ephemeral
        config.httpShouldSetCookies = false
        config.httpCookieStorage = nil
        config.httpMaximumConnectionsPerHost = 4
        config.timeoutIntervalForRequest = 120
        config.timeoutIntervalForResource = 900
        session = URLSession(configuration: config, delegate: StudioNetworkDelegate(), delegateQueue: nil)
        if let data = StudioKeychain.read(), let saved = try? JSONDecoder().decode(StudioSession.self, from: data), saved.expires > Date() {
            identity = saved
        }
    }

    func url(_ path: String) throws -> URL {
        guard let url = URL(string: path, relativeTo: origin)?.absoluteURL,
              url.scheme == "https", url.host == origin.host, url.port == origin.port,
              url.user == nil, url.password == nil else {
            throw StudioFailure(message: "This link does not belong to your Studio.", status: 0)
        }
        return url
    }

    private func request(_ path: String, method: String, body: Data? = nil) throws -> URLRequest {
        var req = URLRequest(url: try url(path))
        req.httpMethod = method
        req.setValue(origin.absoluteString, forHTTPHeaderField: "Origin")
        if identity != nil { req.setValue(cookieHeader, forHTTPHeaderField: "Cookie") }
        req.httpBody = body
        if body != nil { req.setValue("application/json", forHTTPHeaderField: "Content-Type") }
        return req
    }

    private func validate(_ data: Data, _ response: URLResponse) throws {
        guard let response = response as? HTTPURLResponse else { throw StudioFailure(message: "No response from Studio.", status: 0) }
        guard (200..<300).contains(response.statusCode) else {
            let object = (try? JSONSerialization.jsonObject(with: data)) as? [String: Any]
            let message = studioText(object?["error"], fallback: "Studio request failed (\(response.statusCode)).")
            throw StudioFailure(message: response.statusCode == 401 ? "Your session expired. Please sign in again." : message, status: response.statusCode, submissionRejected: object?["submissionState"] as? String == "rejected")
        }
    }

    func data(_ path: String) async throws -> Data {
        let context = cookieHeader
        if activeReads < 4 { activeReads += 1 }
        else { await withCheckedContinuation { waiters.append($0) } }
        defer {
            if waiters.isEmpty { activeReads -= 1 }
            else { waiters.removeFirst().resume() }
        }
        for attempt in 0...2 {
            try Task.checkCancellation()
            guard cookieHeader == context else { throw CancellationError() }
            let (data, response) = try await session.data(for: request(path, method: "GET"))
            guard cookieHeader == context else { throw CancellationError() }
            if let response = response as? HTTPURLResponse, [429, 502, 503, 504].contains(response.statusCode), attempt < 2 {
                try await Task.sleep(nanoseconds: UInt64(attempt + 1) * 1_000_000_000)
                continue
            }
            try validate(data, response)
            return data
        }
        throw StudioFailure(message: "Studio is temporarily unavailable.", status: 503)
    }

    func json(_ path: String, method: String = "GET", body: [String: Any]? = nil, idempotencyKey: String? = nil) async throws -> [String: Any] {
        let result: Data
        if method == "GET" { result = try await data(path) }
        else {
            let payload = try body.map { try JSONSerialization.data(withJSONObject: $0) }
            var req = try request(path, method: method, body: payload)
            if let idempotencyKey { req.setValue(idempotencyKey, forHTTPHeaderField: "Idempotency-Key") }
            let (bytes, response) = try await session.data(for: req)
            try validate(bytes, response)
            result = bytes
        }
        guard let value = try JSONSerialization.jsonObject(with: result) as? [String: Any] else {
            throw StudioFailure(message: "Studio returned an unexpected response.", status: 0)
        }
        return value
    }

    var workspaceMode: String { identity?.mode ?? "owner" }
    var contextKey: String { (identity?.username ?? "anonymous") + "-" + workspaceMode }
    var cookieHeader: String {
        guard let identity else { return "" }
        return ([identity.cookie.isEmpty ? nil : "__Host-studio=" + identity.cookie, identity.hostedCookie.map { "__Host-hosted=" + $0 }].compactMap { $0 }).joined(separator: "; ")
    }
    func privateFile(_ name: String) -> URL { StudioFiles.directory.appendingPathComponent(contextKey + "-" + name) }
    private func cookies(_ response: URLResponse) -> [HTTPCookie] {
        guard let response = response as? HTTPURLResponse else { return [] }
        let headers = response.allHeaderFields.reduce(into: [String: String]()) { $0[String(describing: $1.key)] = String(describing: $1.value) }
        return HTTPCookie.cookies(withResponseHeaderFields: headers, for: origin)
    }
    private func remember(_ value: StudioSession) throws {
        try StudioKeychain.save(JSONEncoder().encode(value)); identity = value
    }
    func signIn(username: String, password: String, workspace: Bool = false, invitation: String? = nil) async throws {
        var values = ["username": username, "password": password]
        if let invitation { values["invitation"] = invitation }
        let payload = try JSONSerialization.data(withJSONObject: values)
        var req = try request(workspace ? (invitation == nil ? "/accounts/login" : "/accounts/register") : "/auth/login", method: "POST", body: payload)
        req.setValue(nil, forHTTPHeaderField: "Cookie")
        let (data, response) = try await session.data(for: req)
        try validate(data, response)
        guard let cookie = cookies(response).first(where: { $0.name == (workspace ? "__Host-hosted" : "__Host-studio") }) else {
            throw StudioFailure(message: "Studio did not create a sign-in session.", status: 0)
        }
        try remember(StudioSession(cookie: workspace ? "" : cookie.value, expires: cookie.expiresDate ?? Date().addingTimeInterval(43200), username: username, hostedCookie: workspace ? cookie.value : nil, mode: workspace ? "workspace" : "owner"))
        if workspace { try await enterWorkspace() }
    }
    func enterWorkspace() async throws {
        for _ in 0..<36 {
            let account = try await json("/accounts/account")
            if account["status"] as? String == "ready" { break }
            if ["failed", "suspended"].contains(account["status"] as? String ?? "") {
                throw StudioFailure(message: "Your workspace could not start. Contact the administrator.", status: 409)
            }
            try await Task.sleep(nanoseconds: 5_000_000_000)
        }
        let entry = try await json("/accounts/enter", method: "POST", body: [:])
        guard let link = entry["url"] as? String, let value = identity else { throw StudioFailure(message: "Workspace entry was incomplete.", status: 0) }
        let (data, response) = try await session.data(for: request(link, method: "GET"))
        guard (response as? HTTPURLResponse)?.statusCode == 303, let cookie = cookies(response).first(where: { $0.name == "__Host-studio" }) else {
            try validate(data, response); throw StudioFailure(message: "Could not open your workspace.", status: 0)
        }
        try remember(StudioSession(cookie: cookie.value, expires: min(value.expires, cookie.expiresDate ?? value.expires), username: value.username, hostedCookie: value.hostedCookie, mode: "workspace"))
    }
    func switchMode(_ mode: String) async throws {
        guard let value = identity, mode != workspaceMode else { return }
        let (data, response) = try await session.data(for: request(mode == "workspace" ? "/accounts/docker" : "/accounts/owner", method: "POST", body: Data("{}".utf8)))
        try validate(data, response)
        guard let cookie = cookies(response).first(where: { $0.name == (mode == "workspace" ? "__Host-hosted" : "__Host-studio") }) else { throw StudioFailure(message: "Mode switch did not create a session.", status: 0) }
        try remember(StudioSession(cookie: mode == "workspace" ? "" : cookie.value, expires: cookie.expiresDate ?? value.expires, username: value.username, hostedCookie: mode == "workspace" ? cookie.value : nil, mode: mode))
        if mode == "workspace" { try await enterWorkspace() }
    }

    func clearSession() { identity = nil; StudioKeychain.clear() }
    func oauthSignIn(provider: String, password: String? = nil) async throws {
        var bytes = [UInt8](repeating: 0, count: 32)
        guard SecRandomCopyBytes(kSecRandomDefault, bytes.count, &bytes) == errSecSuccess else { throw StudioFailure(message: "Could not start secure sign-in.", status: 0) }
        func encoded(_ value: Data) -> String { value.base64EncodedString().replacingOccurrences(of: "+", with: "-").replacingOccurrences(of: "/", with: "_").replacingOccurrences(of: "=", with: "") }
        let verifier = encoded(Data(bytes)), challenge = encoded(Data(SHA256.hash(data: Data(verifier.utf8))))
        var body: [String: Any] = ["provider": provider, "challenge": challenge, "target": "native"]
        if let password { body["link"] = true; body["password"] = password }
        let start = try await json("/accounts/oauth/start", method: "POST", body: body)
        guard let address = start["url"] as? String, let url = URL(string: address), url.scheme == "https", ["appleid.apple.com", "accounts.google.com"].contains(url.host) else { throw StudioFailure(message: "Invalid sign-in provider link.", status: 0) }
        let returned = try await StudioOAuthBrowser.shared.open(url)
        guard returned.scheme == "art.lazying.lazyedit", returned.host == "auth", let ticket = URLComponents(url: returned, resolvingAgainstBaseURL: false)?.queryItems?.first(where: {$0.name == "ticket"})?.value else { throw StudioFailure(message: "Sign-in was incomplete.", status: 0) }
        let payload = try JSONSerialization.data(withJSONObject: ["ticket": ticket, "verifier": verifier])
        let (data, response) = try await session.data(for: request("/accounts/oauth/redeem", method: "POST", body: payload))
        try validate(data, response)
        guard let result = try JSONSerialization.jsonObject(with: data) as? [String: Any], let username = result["username"] as? String, let cookie = cookies(response).first(where: {$0.name == "__Host-hosted"}) else { throw StudioFailure(message: "Studio did not create a sign-in session.", status: 0) }
        try remember(StudioSession(cookie: "", expires: cookie.expiresDate ?? Date().addingTimeInterval(43200), username: username, hostedCookie: cookie.value, mode: "workspace"))
        try await enterWorkspace()
    }
    func signOut() async throws {
        _ = try await json("/auth/logout", method: "POST", body: [:])
        clearSession()
    }

    var webCookies: [HTTPCookie] {
        guard let identity else { return [] }
        let seconds = max(0, Int(identity.expires.timeIntervalSinceNow))
        return cookieHeader.components(separatedBy: "; ").flatMap { value in
            HTTPCookie.cookies(withResponseHeaderFields: ["Set-Cookie": "\(value); Path=/; Secure; HttpOnly; SameSite=Strict; Max-Age=\(seconds)"], for: origin)
        }
    }
    var webCookie: HTTPCookie? { webCookies.first }

    func chunk(uploadID: String, offset: Int64, bytes: Data, progress: @escaping (Int64) -> Void) async throws -> Int64 {
        var req = try request("/v1/studio/upload-part?uploadId=\(uploadID)", method: "PUT")
        req.setValue("application/octet-stream", forHTTPHeaderField: "Content-Type")
        req.setValue(String(offset), forHTTPHeaderField: "Upload-Offset")
        let delegate = StudioUploadProgress(report: progress)
        let (data, response) = try await session.upload(for: req, from: bytes, delegate: delegate)
        try validate(data, response)
        guard let object = try JSONSerialization.jsonObject(with: data) as? [String: Any], let position = object["offset"] as? Int64 else {
            throw StudioFailure(message: "Upload acknowledgement was incomplete. Resume to check the saved position.", status: 0)
        }
        return position
    }
}

@MainActor
final class StudioOAuthBrowser: NSObject, ASWebAuthenticationPresentationContextProviding {
    static let shared = StudioOAuthBrowser()
    private var browser: ASWebAuthenticationSession?
    func presentationAnchor(for session: ASWebAuthenticationSession) -> ASPresentationAnchor {
        UIApplication.shared.connectedScenes.compactMap {$0 as? UIWindowScene}.flatMap { $0.windows }.first(where: {$0.isKeyWindow}) ?? UIWindow()
    }
    func open(_ url: URL) async throws -> URL {
        guard browser == nil else { throw StudioFailure(message: "Sign-in is already open.", status: 0) }
        return try await withCheckedThrowingContinuation { continuation in
            let value = ASWebAuthenticationSession(url: url, callbackURLScheme: "art.lazying.lazyedit") { [weak self] url, error in
                Task { @MainActor in
                    self?.browser = nil
                    if let url { continuation.resume(returning: url) }
                    else { continuation.resume(throwing: error ?? StudioFailure(message: "Sign-in was cancelled.", status: 0)) }
                }
            }
            browser = value; value.presentationContextProvider = self
            if !value.start() { browser = nil; continuation.resume(throwing: StudioFailure(message: "Could not open secure sign-in.", status: 0)) }
        }
    }
}
