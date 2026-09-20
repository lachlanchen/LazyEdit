import Foundation
import Security

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
        if let identity { req.setValue("__Host-studio=" + identity.cookie, forHTTPHeaderField: "Cookie") }
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
        if activeReads < 4 { activeReads += 1 }
        else { await withCheckedContinuation { waiters.append($0) } }
        defer {
            if waiters.isEmpty { activeReads -= 1 }
            else { waiters.removeFirst().resume() }
        }
        for attempt in 0...2 {
            try Task.checkCancellation()
            let (data, response) = try await session.data(for: request(path, method: "GET"))
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

    func signIn(username: String, password: String) async throws {
        let payload = try JSONSerialization.data(withJSONObject: ["username": username, "password": password])
        let (data, response) = try await session.data(for: request("/auth/login", method: "POST", body: payload))
        try validate(data, response)
        guard let response = response as? HTTPURLResponse else { return }
        let headers = response.allHeaderFields.reduce(into: [String: String]()) { $0[String(describing: $1.key)] = String(describing: $1.value) }
        guard let cookie = HTTPCookie.cookies(withResponseHeaderFields: headers, for: origin).first(where: { $0.name == "__Host-studio" }) else {
            throw StudioFailure(message: "Studio did not create a sign-in session.", status: 0)
        }
        let saved = StudioSession(cookie: cookie.value, expires: cookie.expiresDate ?? Date().addingTimeInterval(43200), username: username)
        try StudioKeychain.save(JSONEncoder().encode(saved))
        identity = saved
    }

    func clearSession() { identity = nil; StudioKeychain.clear() }
    func signOut() async throws {
        _ = try await json("/auth/logout", method: "POST", body: [:])
        clearSession()
    }

    var webCookie: HTTPCookie? {
        guard let identity else { return nil }
        let seconds = max(0, Int(identity.expires.timeIntervalSinceNow))
        let header = "__Host-studio=\(identity.cookie); Path=/; Secure; HttpOnly; SameSite=Strict; Max-Age=\(seconds)"
        return HTTPCookie.cookies(withResponseHeaderFields: ["Set-Cookie": header], for: origin).first
    }

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
