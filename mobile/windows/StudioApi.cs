using System.IO;
using System.Net;
using System.Net.Http;
using System.Security.Cryptography;
using System.Text;
using System.Text.Json.Nodes;

namespace LazyEditStudio;

public sealed record StudioSession(string Username, string Mode, string Cookie,
    string HostedCookie, DateTimeOffset Expires);

public sealed class StudioException(string message, int status = 0, bool submissionRejected = false) : Exception(message)
{
    public int Status { get; } = status;
    public bool SubmissionRejected { get; } = submissionRejected;
}

public sealed class StudioApi : IDisposable
{
    public static readonly Uri Origin = new("https://edit.lazying.art");
    public static readonly string StateRoot = Path.Combine(
        Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData), "LazyEditStudio");
    private readonly HttpClient client = new(new HttpClientHandler {
        AllowAutoRedirect = false, UseCookies = false }) { Timeout = TimeSpan.FromMinutes(3) };
    public StudioSession? Session { get; private set; }
    public string Context => Convert.ToHexString(SHA256.HashData(Encoding.UTF8.GetBytes(
        (Session?.Username ?? "anonymous") + "-" + (Session?.Mode ?? "workspace")))).Substring(0, 24);
    public string CookieHeader => string.Join("; ", new[] {
        string.IsNullOrEmpty(Session?.Cookie) ? "" : "__Host-studio=" + Session.Cookie,
        string.IsNullOrEmpty(Session?.HostedCookie) ? "" : "__Host-hosted=" + Session.HostedCookie
    }.Where(x => x.Length > 0));
    public string ContextPath(string name) => Path.Combine(StateRoot, Context + "-" + name);

    public StudioApi(bool restore = true)
    {
        Directory.CreateDirectory(StateRoot);
        if (restore) try {
            var bytes = ProtectedData.Unprotect(File.ReadAllBytes(Path.Combine(StateRoot, "session.bin")), null, DataProtectionScope.CurrentUser);
            var session = System.Text.Json.JsonSerializer.Deserialize<StudioSession>(bytes);
            if (session?.Expires > DateTimeOffset.UtcNow) Session = session;
        } catch (Exception e) when (e is IOException or CryptographicException or System.Text.Json.JsonException) { }
    }

    public static Uri SafeUrl(string path)
    {
        var url = new Uri(Origin, path);
        if (url.Scheme != "https" || url.Host != Origin.Host || url.Port != Origin.Port
            || url.UserInfo.Length != 0) throw new StudioException("This link does not belong to your Studio.");
        return url;
    }

    private async Task<HttpResponseMessage> Send(string path, HttpMethod method,
        HttpContent? content = null, string? key = null, long? offset = null, bool authenticated = true)
    {
        using var request = new HttpRequestMessage(method, SafeUrl(path));
        request.Headers.Add("Origin", Origin.ToString().TrimEnd('/'));
        if (authenticated && Session != null) request.Headers.Add("Cookie", CookieHeader);
        if (key != null) request.Headers.Add("Idempotency-Key", key);
        if (offset != null) request.Headers.Add("Upload-Offset", offset.Value.ToString());
        request.Content = content;
        return await client.SendAsync(request);
    }

    private static async Task<JsonObject> Decode(HttpResponseMessage response)
    {
        var text = await response.Content.ReadAsStringAsync();
        JsonObject? result = null;
        try { result = JsonNode.Parse(text) as JsonObject; } catch (System.Text.Json.JsonException) { }
        if (!response.IsSuccessStatusCode) {
            var error = result?["error"];
            var message = error is JsonObject obj ? obj["message"]?.ToString() : error?.ToString();
            throw new StudioException((int)response.StatusCode == 401 ? "Your session expired. Please sign in again."
                : message ?? $"Studio request failed ({(int)response.StatusCode}).", (int)response.StatusCode,
                result?["submissionState"]?.ToString() == "rejected");
        }
        return result ?? throw new StudioException("Studio returned an unexpected response.");
    }

    public async Task<JsonObject> Json(string path, JsonObject? body = null, string? key = null)
    {
        using var response = await Send(path, body == null ? HttpMethod.Get : HttpMethod.Post,
            body == null ? null : new StringContent(body.ToJsonString(), Encoding.UTF8, "application/json"), key);
        return await Decode(response);
    }

    private static Cookie ResponseCookie(HttpResponseMessage response, string name)
    {
        var cookies = new CookieContainer();
        if (response.Headers.TryGetValues("Set-Cookie", out var headers))
            foreach (var value in headers) cookies.SetCookies(Origin, value);
        return cookies.GetCookies(Origin).Cast<Cookie>().SingleOrDefault(c => c.Name == name)
            ?? throw new StudioException("Studio did not create a sign-in session.");
    }

    private void Remember(StudioSession session)
    {
        var bytes = ProtectedData.Protect(System.Text.Json.JsonSerializer.SerializeToUtf8Bytes(session), null, DataProtectionScope.CurrentUser);
        AtomicWrite(Path.Combine(StateRoot, "session.bin"), bytes);
        Session = session;
    }

    public static void AtomicWrite(string path, byte[] bytes)
    {
        var tmp = path + ".tmp";
        File.WriteAllBytes(tmp, bytes);
        File.Move(tmp, path, true);
    }

    public async Task Login(string username, string password, bool workspace, string invitation = "")
    {
        Session = null;
        var body = new JsonObject { ["username"] = username, ["password"] = password };
        if (invitation.Length > 0) body["invitation"] = invitation;
        using var response = await Send(workspace ? (invitation.Length > 0 ? "/accounts/register" : "/accounts/login") : "/auth/login",
            HttpMethod.Post, new StringContent(body.ToJsonString(), Encoding.UTF8, "application/json"), authenticated: false);
        await Decode(response);
        var cookie = ResponseCookie(response, workspace ? "__Host-hosted" : "__Host-studio");
        Remember(new(username, workspace ? "workspace" : "owner", workspace ? "" : cookie.Value,
            workspace ? cookie.Value : "", cookie.Expires == DateTime.MinValue ? DateTimeOffset.UtcNow.AddHours(12) : cookie.Expires.ToUniversalTime()));
        if (workspace) await EnterWorkspace();
    }

    public async Task EnterWorkspace()
    {
        for (var attempt = 0; attempt < 36; attempt++) {
            var account = await Json("/accounts/account");
            if (account["status"]?.ToString() == "ready") break;
            if (account["status"]?.ToString() is "failed" or "suspended") throw new StudioException("Your workspace could not start. Contact the administrator.");
            if (attempt == 35) throw new StudioException("Your workspace is still starting. Sign in again shortly.");
            await Task.Delay(5000);
        }
        var entry = await Json("/accounts/enter", new());
        using var response = await Send(entry["url"]?.ToString() ?? throw new StudioException("Workspace entry is incomplete."), HttpMethod.Get);
        if (response.StatusCode != HttpStatusCode.SeeOther) { await Decode(response); throw new StudioException("Could not enter your private workspace."); }
        var cookie = ResponseCookie(response, "__Host-studio");
        var current = Session ?? throw new StudioException("Sign in again.");
        Remember(current with { Cookie = cookie.Value, Expires = cookie.Expires == DateTime.MinValue ? current.Expires : cookie.Expires.ToUniversalTime() });
    }

    public async Task SwitchMode(string mode)
    {
        var current = Session ?? throw new StudioException("Sign in again.");
        using var response = await Send(mode == "owner" ? "/accounts/owner" : "/accounts/docker", HttpMethod.Post,
            new StringContent("{}", Encoding.UTF8, "application/json"));
        await Decode(response);
        var cookie = ResponseCookie(response, mode == "owner" ? "__Host-studio" : "__Host-hosted");
        Remember(current with { Mode = mode, Cookie = mode == "owner" ? cookie.Value : "", HostedCookie = mode == "owner" ? "" : cookie.Value });
        if (mode == "workspace") await EnterWorkspace();
    }

    public async Task Logout()
    {
        try { await Json("/auth/logout", new()); } finally {
            Session = null; File.Delete(Path.Combine(StateRoot, "session.bin"));
        }
    }

    public async Task DiscardUpload()
    {
        var path = ContextPath("upload.json");
        if (!File.Exists(path)) return;
        var saved = JsonNode.Parse(File.ReadAllText(path))!.AsObject();
        using var response = await Send("/v1/studio/upload?uploadId=" + Uri.EscapeDataString(saved["id"]!.ToString()), HttpMethod.Delete);
        await Decode(response);
        File.Delete(path);
    }

    public async Task<JsonObject> Upload(string file, Action<double> progress)
    {
        var info = new FileInfo(file);
        if (!info.Exists || !new[] { ".mov", ".mp4", ".m4v", ".webm" }.Contains(info.Extension.ToLowerInvariant()))
            throw new StudioException("Choose an MP4, MOV, M4V or WebM video.");
        var receiptPath = ContextPath("upload.json");
        JsonObject? saved = null;
        if (File.Exists(receiptPath)) saved = JsonNode.Parse(File.ReadAllText(receiptPath)) as JsonObject;
        if (saved != null && (saved["path"]?.ToString() != info.FullName || saved["size"]?.GetValue<long>() != info.Length
            || saved["modified"]?.GetValue<long>() != info.LastWriteTimeUtc.Ticks))
            throw new StudioException("A different upload is saved. Resume that file or explicitly discard the pending upload.");
        if (saved == null) {
            var allocated = await Json("/v1/studio/uploads", new() { ["filename"] = info.Name, ["title"] = info.Name, ["size"] = info.Length });
            saved = new() { ["path"] = info.FullName, ["size"] = info.Length, ["modified"] = info.LastWriteTimeUtc.Ticks,
                ["id"] = allocated["uploadId"]?.ToString() ?? throw new StudioException("Upload allocation was incomplete.") };
            AtomicWrite(receiptPath, Encoding.UTF8.GetBytes(saved.ToJsonString()));
        }
        var id = saved["id"]!.ToString();
        var position = await Json("/v1/studio/upload?uploadId=" + Uri.EscapeDataString(id));
        if (position["receipt"] is JsonObject existing) { File.Delete(receiptPath); return existing; }
        var offset = position["offset"]?.GetValue<long>() ?? 0;
        if (offset < 0 || offset > info.Length) throw new StudioException("Invalid saved upload position.");
        await using var stream = info.OpenRead();
        stream.Position = offset;
        var buffer = new byte[8 * 1024 * 1024];
        while (offset < info.Length) {
            var count = await stream.ReadAsync(buffer.AsMemory(0, (int)Math.Min(buffer.Length, info.Length - offset)));
            if (count == 0) throw new StudioException("Video changed while uploading.");
            using var bytes = new ByteArrayContent(buffer, 0, count);
            bytes.Headers.ContentType = new("application/octet-stream");
            using var response = await Send("/v1/studio/upload-part?uploadId=" + Uri.EscapeDataString(id), HttpMethod.Put, bytes, offset: offset);
            var acknowledged = (await Decode(response))["offset"]?.GetValue<long>();
            if (acknowledged != offset + count) throw new StudioException("Upload acknowledgement changed. Resume to reconcile the saved position.");
            offset += count; progress((double)offset / info.Length);
        }
        var final = await Json("/v1/studio/upload-complete", new() { ["uploadId"] = id });
        if (final["videoId"] == null && final["video_id"] == null) throw new StudioException("Upload receipt is missing. Resume before retrying.");
        File.Delete(receiptPath); return final;
    }

    public void Dispose() => client.Dispose();
}
