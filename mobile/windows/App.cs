using System.IO;
using System.Text;
using System.Text.Json.Nodes;
using System.Windows;
using System.Windows.Controls;
using System.Windows.Media;
using System.Windows.Media.Imaging;
using Microsoft.Web.WebView2.Core;
using Microsoft.Web.WebView2.Wpf;
using Microsoft.Win32;

namespace LazyEditStudio;

public static class Program
{
    [STAThread]
    public static int Main(string[] args)
    {
        var application = new Application { ShutdownMode = ShutdownMode.OnMainWindowClose };
        if (args.Contains("--contract-test")) {
            try {
                if (StudioApi.SafeUrl("/v1/studio/account").Host != StudioApi.Origin.Host) return 1;
                foreach (var bad in new[] { "https://example.com/", "https://user@edit.lazying.art/", "http://edit.lazying.art/", "https://edit.lazying.art:444/" }) {
                    try { StudioApi.SafeUrl(bad); return 2; } catch (StudioException) { }
                }
                var window = new MainWindow();
                if (window.Title != "LazyEdit Studio" || window.Content is not DockPanel) return 3;
                File.WriteAllText(Path.Combine(StudioApi.StateRoot, "contract-test.txt"), "Native WPF controls and authenticated-origin contract passed.\n");
                window.Close(); return 0;
            } catch { return 4; }
        }
        var check = Array.IndexOf(args, "--workspace-check");
        var main = new MainWindow(check >= 0 && args.Length > check + 1 ? args[check + 1] : null);
        application.Run(main);
        return 0;
    }
}

public sealed class MainWindow : Window
{
    private readonly StudioApi api = new();
    private readonly DockPanel root = new();
    private readonly StackPanel content = new() { Margin = new Thickness(26), MaxWidth = 1180, HorizontalAlignment = HorizontalAlignment.Stretch };
    private readonly TextBlock status = new() { Margin = new Thickness(20, 8, 20, 8), TextWrapping = TextWrapping.Wrap };
    private readonly System.Windows.Threading.DispatcherTimer timer = new() { Interval = TimeSpan.FromSeconds(30) };
    private readonly Dictionary<string, string> locale = new();
    private string language = "en", page = "Studio";
    private readonly List<Window> viewers = new();
    private bool busy, canPublish;
    private JsonObject account = new();
    private int selectedVideo;
    private JsonObject choices = new();
    private string reviewedDigest = "";
    private Button? sendButton;

    public MainWindow(string? checkCredentials = null)
    {
        Title = "LazyEdit Studio"; Width = 1160; Height = 850; MinWidth = 800; MinHeight = 620;
        Background = new SolidColorBrush(Color.FromRgb(247, 248, 250));
        FontFamily = new FontFamily("Segoe UI"); FontSize = 14; Content = root;
        LoadLanguage();
        DockPanel.SetDock(status, Dock.Bottom); root.Children.Add(status);
        var scroll = new ScrollViewer { VerticalScrollBarVisibility = ScrollBarVisibility.Auto, Content = content };
        root.Children.Add(scroll);
        timer.Tick += async (_, _) => { if (!busy && IsActive && api.Session != null && page == "Activity") await Guard(Activity); };
        Activated += (_, _) => timer.Start(); Deactivated += (_, _) => timer.Stop();
        Closed += (_, _) => { timer.Stop(); api.Dispose(); };
        Loaded += async (_, _) => {
            if (checkCredentials != null) {
                try { await CheckWorkspace(checkCredentials); Application.Current.Shutdown(0); }
                catch (Exception e) { File.WriteAllText(Path.Combine(StudioApi.StateRoot, "workspace-check.txt"), "FAILED: " + e.Message); Application.Current.Shutdown(5); }
            } else if (api.Session == null) Login(); else await Guard(async () => { await Identity(); Navigation(); await Library(); });
        };
    }

    private void Capture(string name)
    {
        UpdateLayout();
        var bitmap = new RenderTargetBitmap((int)ActualWidth, (int)ActualHeight, 96, 96, PixelFormats.Pbgra32);
        bitmap.Render(this); var encoder = new PngBitmapEncoder(); encoder.Frames.Add(BitmapFrame.Create(bitmap));
        using var stream = File.Create(Path.Combine(StudioApi.StateRoot, name + ".png")); encoder.Save(stream);
    }
    private async Task CheckWorkspace(string path)
    {
        // Explicit isolated reviewer qualification: no upload, preparation or social post.
        var credential = JsonNode.Parse(File.ReadAllText(path))!.AsObject();
        if (credential["username"]!.ToString() == "lachlanchen") throw new StudioException("Qualification requires an isolated reviewer.");
        await api.Login(credential["username"]!.ToString(), credential["password"]!.ToString(), true);
        await Identity(); if (canPublish) throw new StudioException("Reviewer unexpectedly has publishing permission.");
        Navigation(); await Library(); Capture("windows-native-library");
        var videos = (await api.Json("/api/videos"))["videos"]!.AsArray();
        selectedVideo = videos[0]!["id"]!.GetValue<int>(); await Compose(); Capture("windows-native-composer");
        var plan = await api.Json($"/v1/studio/videos/{selectedVideo}/plan", choices);
        if (plan["planDigest"]?.ToString().Length != 64) throw new StudioException("Invalid plan digest.");
        await Web($"/editor?videoId={selectedVideo}", true, videos[0]!["title"]?.ToString());
        await Account(); Capture("windows-native-account");
        await api.Logout();
        File.WriteAllText(Path.Combine(StudioApi.StateRoot, "workspace-check.txt"), "PASS: reviewer login, private library, native composer, server plan, hydrated editor, account isolation and logout. No preparation or publication submitted.\n");
    }

    private string T(string value) => locale.GetValueOrDefault(value, value);
    private void LoadLanguage()
    {
        var preference = Path.Combine(StudioApi.StateRoot, "language.txt");
        language = File.Exists(preference) ? File.ReadAllText(preference).Trim() : "en";
        try {
            var values = JsonNode.Parse(File.ReadAllText(Path.Combine(AppContext.BaseDirectory, "Locales", language + ".json"))) as JsonObject;
            locale.Clear(); if (values != null) foreach (var pair in values) locale[pair.Key] = pair.Value?.ToString() ?? pair.Key;
        } catch (IOException) { locale.Clear(); }
        FlowDirection = language == "ar" ? FlowDirection.RightToLeft : FlowDirection.LeftToRight;
    }
    private TextBlock Text(string value, double size = 14) => new() { Text = T(value), FontSize = size, TextWrapping = TextWrapping.Wrap, Margin = new Thickness(0, 5, 0, 10) };
    private Button Button(string label, Func<Task> action)
    {
        var button = new Button { Content = T(label), Padding = new Thickness(15, 9, 15, 9), Margin = new Thickness(0, 4, 8, 6), HorizontalAlignment = HorizontalAlignment.Left };
        button.Click += async (_, _) => await Guard(action); return button;
    }
    private async Task Guard(Func<Task> action)
    {
        if (busy) return; busy = true; status.Text = T("Loading…");
        content.IsEnabled = false;
        try { await action(); status.Text = ""; }
        catch (Exception error) { status.Text = error.Message; if (error is StudioException { Status: 401 }) Login(); }
        finally { busy = false; content.IsEnabled = true; }
    }
    private void Clear(string title) { content.Children.Clear(); content.Children.Add(Text(title, 30)); }
    private void Languages()
    {
        var box = new ComboBox { Width = 210, HorizontalAlignment = HorizontalAlignment.Left, Margin = new Thickness(0, 6, 0, 15) };
        foreach (var code in new[] { "en", "zh-Hans", "zh-Hant", "ja", "ko", "vi", "ar", "fr", "es", "de", "ru" }) box.Items.Add(code);
        box.SelectedItem = language;
        box.SelectionChanged += async (_, _) => {
            language = box.SelectedItem?.ToString() ?? "en";
            File.WriteAllText(Path.Combine(StudioApi.StateRoot, "language.txt"), language); LoadLanguage();
            if (api.Session == null) Login();
            else { Navigation(); await Guard(async () => { if (page == "Activity") await Activity(); else if (page == "Upload") Upload(); else if (page == "Account") await Account(); else await Library(); }); }
        };
        content.Children.Add(box);
    }
    private void Login()
    {
        var existing = root.Children.OfType<StackPanel>().FirstOrDefault(x => x.Tag as string == "nav");
        if (existing != null) root.Children.Remove(existing);
        Clear("Your stories.\nYour Studio.");
        content.Children.Add(Text("A quiet space to edit, prepare and share your videos.")); Languages();
        var username = new TextBox { MaxWidth = 460, HorizontalAlignment = HorizontalAlignment.Stretch, Margin = new Thickness(0, 4, 0, 12) };
        var password = new PasswordBox { MaxWidth = 460, HorizontalAlignment = HorizontalAlignment.Stretch, Margin = new Thickness(0, 4, 0, 12) };
        var owner = new CheckBox { Content = T("Existing Pi"), Visibility = Visibility.Collapsed, Margin = new Thickness(0, 6, 0, 12) };
        username.TextChanged += (_, _) => { owner.Visibility = username.Text.Trim() == "lachlanchen" ? Visibility.Visible : Visibility.Collapsed; if (owner.Visibility == Visibility.Collapsed) owner.IsChecked = false; };
        var invitation = new TextBox { MaxWidth = 460, Margin = new Thickness(0, 4, 0, 12) };
        var register = new CheckBox { Content = T("Create account with invitation") };
        content.Children.Add(Text("Username")); content.Children.Add(username);
        content.Children.Add(Text("Password")); content.Children.Add(password); content.Children.Add(owner);
        content.Children.Add(register); content.Children.Add(Text("Invitation code")); content.Children.Add(invitation);
        content.Children.Add(Button("Sign in", async () => {
            var user = username.Text.Trim(); if (user.Length == 0 || password.Password.Length == 0) throw new StudioException("Enter your username and password.");
            await api.Login(user, password.Password, owner.IsChecked != true, register.IsChecked == true ? invitation.Text.Trim() : "");
            password.Clear(); await Identity(); Navigation(); await Library();
        }));
        content.Children.Add(Text("edit.lazying.art"));
    }
    private async Task Identity()
    {
        account = await api.Json("/auth/me");
        canPublish = account["capabilities"]?["publishing"]?.GetValue<bool>() == true;
    }
    private void Navigation()
    {
        var previous = root.Children.OfType<StackPanel>().FirstOrDefault(x => x.Tag as string == "nav");
        if (previous != null) root.Children.Remove(previous);
        var sidebar = new StackPanel { Tag = "nav", Width = 172, Margin = new Thickness(18, 24, 10, 0) };
        sidebar.Children.Add(Text("LazyEdit\nStudio", 24));
        foreach (var name in new[] { "Studio", "Upload", "Activity", "Account" }) sidebar.Children.Add(Button(name, async () => {
            page = name; switch (name) { case "Studio": await Library(); break; case "Upload": Upload(); break; case "Activity": await Activity(); break; default: await Account(); break; }
        }));
        DockPanel.SetDock(sidebar, Dock.Left); root.Children.Insert(1, sidebar);
    }
    private async Task Library(bool hidden = false)
    {
        Clear(hidden ? "Removed videos" : "Your Studio");
        var data = await api.Json(hidden ? "/api/videos?hidden=true" : "/api/videos");
        var search = new TextBox { Margin = new Thickness(0, 0, 0, 12) }; content.Children.Add(search);
        var list = new ListBox { MaxHeight = 560, HorizontalContentAlignment = HorizontalAlignment.Stretch };
        var videos = (data["videos"] as JsonArray ?? new()).OfType<JsonObject>().ToArray();
        void Filter() {
            list.Items.Clear();
            foreach (var video in videos.Where(v => (v["title"]?.ToString() ?? "").Contains(search.Text, StringComparison.CurrentCultureIgnoreCase))) {
                var item = new ListBoxItem { Tag = video, Content = new TextBlock { Text = (video["title"]?.ToString() ?? "Video") + "\n" + video["created_at"], TextWrapping = TextWrapping.Wrap, Margin = new Thickness(8) } };
                list.Items.Add(item);
            }
        }
        search.TextChanged += (_, _) => Filter(); Filter(); content.Children.Add(list);
        content.Children.Add(Button("Edit & preview", async () => {
            if (list.SelectedItem is not ListBoxItem { Tag: JsonObject video }) throw new StudioException("Select a video.");
            selectedVideo = video["id"]!.GetValue<int>(); await Compose();
        }));
        content.Children.Add(Button(hidden ? "Restore" : "Remove", async () => {
            if (list.SelectedItem is not ListBoxItem { Tag: JsonObject video }) throw new StudioException("Select a video.");
            if (MessageBox.Show(T("Remove") + " / " + T("Restore") + "?", Title, MessageBoxButton.YesNo) != MessageBoxResult.Yes) return;
            await api.Json($"/v1/studio/videos/{video["id"]}/visibility", new() { ["hidden"] = !hidden }); await Library(hidden);
        }));
        content.Children.Add(Button(hidden ? "Studio" : "Removed videos", () => Library(!hidden)));
        content.Children.Add(Button("Refresh", () => Library(hidden)));
        content.Children.Add(Text(videos.Length == 0 ? "Your next story starts here" : $"{videos.Length} videos"));
    }
    private void Upload()
    {
        Clear("Upload"); content.Children.Add(Text("Choose a video from Photos or Files to add it to your Studio."));
        var selected = new TextBlock { TextWrapping = TextWrapping.Wrap, Margin = new Thickness(0, 10, 0, 20) };
        var progress = new ProgressBar { Minimum = 0, Maximum = 1, Height = 8, Margin = new Thickness(0, 8, 0, 18) };
        var pending = api.ContextPath("upload.json");
        if (File.Exists(pending)) selected.Text = JsonNode.Parse(File.ReadAllText(pending))?["path"]?.ToString() ?? "";
        content.Children.Add(Button("Files", () => { var picker = new OpenFileDialog { Filter = "Videos|*.mp4;*.mov;*.m4v;*.webm", CheckFileExists = true }; if (picker.ShowDialog(this) == true) selected.Text = picker.FileName; return Task.CompletedTask; }));
        content.Children.Add(selected); content.Children.Add(progress);
        content.Children.Add(Button("Discard pending upload", async () => {
            if (MessageBox.Show("Discard only the incomplete upload? Your source file stays unchanged.", Title, MessageBoxButton.YesNo) != MessageBoxResult.Yes) return;
            await api.DiscardUpload(); selected.Text = ""; progress.Value = 0;
        }));
        content.Children.Add(Button("Upload / Resume", async () => {
            if (selected.Text.Length == 0) throw new StudioException("Choose a video first.");
            await api.Upload(selected.Text, value => { progress.Value = value; status.Text = $"{value:P0}"; });
            page = "Studio"; await Library();
        }));
    }
    private async Task Activity()
    {
        Clear("Activity"); var response = await api.Json("/api/autopublish/queue");
        foreach (var job in (response["jobs"] as JsonArray ?? new()).OfType<JsonObject>().Reverse().Take(60)) {
            content.Children.Add(Text($"{job["video_title"] ?? job["filename"] ?? job["id"]}\n{job["status"]} · {job["detail"]}"));
            if (job["attention"] is JsonObject attention) {
                content.Children.Add(Text(attention["message"]?.ToString() ?? "Platform login is required."));
                if (canPublish) content.Children.Add(Button("Platform accounts", () => Web("/platforms")));
            }
        }
        content.Children.Add(Button("Refresh", Activity));
    }
    private async Task Account()
    {
        Clear("Account"); await Identity();
        content.Children.Add(Text(api.Session?.Username ?? ""));
        content.Children.Add(Text(api.Session?.Mode == "owner" ? "Existing Pi workspace" : "Private Docker workspace")); Languages();
        if (canPublish) content.Children.Add(Button("Platform accounts", () => Web("/platforms")));
        content.Children.Add(Button("Account settings", () => Web("/home")));
        if (api.Session?.Username == "lachlanchen") content.Children.Add(Button(api.Session.Mode == "owner" ? "Switch to private Docker workspace" : "Switch to existing Pi workspace", async () => {
            await api.SwitchMode(api.Session!.Mode == "owner" ? "workspace" : "owner"); await Identity(); await Account();
        }));
        content.Children.Add(Button("Sign out", async () => { foreach (var viewer in viewers.ToArray()) viewer.Close(); await api.Logout(); Login(); }));
    }
    private void Field(string label, string key, bool multiline = false)
    {
        content.Children.Add(Text(label));
        var input = new TextBox { Text = choices[key]?.ToString() ?? "", AcceptsReturn = multiline, TextWrapping = TextWrapping.Wrap,
            MinHeight = multiline ? 85 : 26, Margin = new Thickness(0, 0, 0, 12) };
        input.TextChanged += (_, _) => { choices[key] = input.Text; Changed(); }; content.Children.Add(input);
    }
    private void Toggle(string label, string key)
    {
        var input = new CheckBox { Content = T(label), IsChecked = choices[key]?.GetValue<bool>() == true, Margin = new Thickness(0, 6, 0, 10) };
        input.Click += (_, _) => { choices[key] = input.IsChecked == true; Changed(); }; content.Children.Add(input);
    }
    private void Number(string label, string key, double min, double max)
    {
        content.Children.Add(Text(label)); var input = new TextBox { Text = choices[key]?.ToString() ?? "", Width = 110, HorizontalAlignment = HorizontalAlignment.Left, Margin = new Thickness(0, 0, 0, 12) };
        input.TextChanged += (_, _) => { if (double.TryParse(input.Text, System.Globalization.NumberStyles.Float, System.Globalization.CultureInfo.InvariantCulture, out var value) && value >= min && value <= max) { choices[key] = key is "rows" or "sessionID" ? JsonValue.Create((int)value) : JsonValue.Create(value); Changed(); } else status.Text = $"{label}: {min}–{max}"; }; content.Children.Add(input);
    }
    private void Choice(string label, string key, string[] values)
    {
        content.Children.Add(Text(label)); var input = new ComboBox { Width = 240, HorizontalAlignment = HorizontalAlignment.Left, Margin = new Thickness(0, 0, 0, 12) };
        foreach (var value in values) input.Items.Add(value); input.SelectedItem = choices[key]?.ToString();
        input.SelectionChanged += (_, _) => { choices[key] = input.SelectedItem?.ToString() ?? values[0]; Changed(); }; content.Children.Add(input);
    }
    private void Changed()
    {
        reviewedDigest = ""; if (sendButton != null) sendButton.IsEnabled = false;
        StudioApi.AtomicWrite(api.ContextPath($"choices-{selectedVideo}.json"), Encoding.UTF8.GetBytes(choices.ToJsonString()));
    }
    private async Task Compose()
    {
        Clear("Edit & preview");
        var configuration = await api.Json($"/v1/studio/videos/{selectedVideo}/composer");
        canPublish = configuration["capabilities"]?["publishing"]?.GetValue<bool>() == true;
        choices = configuration["defaults"]?.DeepClone() as JsonObject ?? throw new StudioException("Missing editor defaults.");
        var saved = api.ContextPath($"choices-{selectedVideo}.json");
        if (File.Exists(saved)) choices = JsonNode.Parse(File.ReadAllText(saved)) as JsonObject ?? choices;
        if (!canPublish) choices["platforms"] = new JsonArray();
        var portrait = configuration["geometry"]?["portrait"]?.GetValue<bool>() == true;
        if (portrait) choices["background"] = "off";
        reviewedDigest = ""; sendButton = null;
        content.Children.Add(Text("Choose how to prepare this video. Saved website defaults are not changed."));
        Toggle("Burn subtitles", "burnSubtitles");
        content.Children.Add(Text("Subtitle languages (bottom-to-top, comma separated)"));
        var languages = new TextBox { Text = string.Join(",", (choices["languages"] as JsonArray ?? new()).Select(x => x!.ToString())), Margin = new Thickness(0, 0, 0, 12) };
        languages.TextChanged += (_, _) => { choices["languages"] = new JsonArray(languages.Text.Split(',', StringSplitOptions.TrimEntries | StringSplitOptions.RemoveEmptyEntries).Select(x => (JsonNode?)JsonValue.Create(x)).ToArray()); Changed(); }; content.Children.Add(languages);
        Number("Subtitle lift ratio", "lift", 0, .4); Number("Subtitle rows", "rows", 1, 8);
        Number("Subtitle font size", "fontScale", .6, 2.5); Toggle("Bold text", "fontBold"); Toggle("Bold outline", "outlineBold");
        Toggle("Logo", "logo"); Choice("Logo position", "logoPosition", ["top-right", "top-left", "bottom-right", "bottom-left"]);
        if (!portrait) { Choice("Portrait background", "background", ["off", "bottom", "center"]); Number("Bottom space", "bottomSpace", 0, .8); }
        Field("Story, names, technical terms or reference script", "context", true);
        Field("Metadata direction", "metadataDirection", true);
        Toggle("Correct subtitles", "correct"); Toggle("Use context for metadata", "contextForMetadata");
        Choice("Publication run", "mode", ["new", "reuse"]); Number("Run number (reuse)", "sessionID", 0, 999999);
        Choice("Category", "category", ["", "simplelife", "lazyingart", "lalachan", "musia", "lalamv"]);
        if (canPublish) {
            content.Children.Add(Text("Select platforms"));
            foreach (var platform in new[] { "shipinhao", "instagram", "youtube", "douyin", "xiaohongshu", "bilibili" }) {
                var box = new CheckBox { Content = platform, IsChecked = (choices["platforms"] as JsonArray)?.Any(p => p?.ToString() == platform) == true, Margin = new Thickness(0, 5, 0, 5) };
                box.Click += (_, _) => { var platforms = ((choices["platforms"] as JsonArray ?? new()).Select(p => p!.ToString()).Where(p => p != platform)).ToList(); if (box.IsChecked == true) platforms.Add(platform); choices["platforms"] = new JsonArray(platforms.Select(p => (JsonNode?)JsonValue.Create(p)).ToArray()); Changed(); }; content.Children.Add(box);
            }
        }
        content.Children.Add(Button("Full editor", () => Web($"/editor?videoId={selectedVideo}")));
        content.Children.Add(Button("Review plan", async () => {
            var plan = await api.Json($"/v1/studio/videos/{selectedVideo}/plan", choices);
            reviewedDigest = plan["planDigest"]?.ToString() ?? throw new StudioException("Missing plan receipt.");
            var summary = plan["summary"]?.ToJsonString() ?? "";
            MessageBox.Show(summary, T("Review plan"), MessageBoxButton.OK); sendButton!.IsEnabled = true;
        }));
        sendButton = Button(canPublish ? "Process and publish" : "Process & preview", Submit); sendButton.IsEnabled = false; content.Children.Add(sendButton);
        var pending = api.ContextPath($"submission-{selectedVideo}.json");
        if (File.Exists(pending)) content.Children.Add(Button("Check saved submission", async () => {
            var intent = JsonNode.Parse(File.ReadAllText(pending))!.AsObject();
            var response = await api.Json($"/v1/studio/videos/{selectedVideo}/submission?key=" + Uri.EscapeDataString(intent["key"]!.ToString()));
            if (response["result"] is JsonObject) File.Delete(pending);
            else if (response["state"]?.ToString() == "not_submitted" && MessageBox.Show("Retry the same saved request?", Title, MessageBoxButton.YesNo) == MessageBoxResult.Yes) {
                var receipt = await api.Json($"/v1/studio/videos/{selectedVideo}/submit", intent["body"]!.DeepClone().AsObject(), intent["key"]!.ToString());
                File.Delete(pending); response = receipt;
            }
            MessageBox.Show(response.ToJsonString(), "Saved task");
        }));
    }
    private async Task Submit()
    {
        if (reviewedDigest.Length == 0) throw new StudioException("Review the current plan first.");
        if (MessageBox.Show(T(canPublish ? "Process and publish" : "Process & preview") + "?", T("Review plan"), MessageBoxButton.YesNo) != MessageBoxResult.Yes) return;
        var path = api.ContextPath($"submission-{selectedVideo}.json");
        if (File.Exists(path)) throw new StudioException("A saved submission exists. Check its receipt before repeating.");
        var key = Guid.NewGuid().ToString();
        var body = new JsonObject { ["form"] = choices.DeepClone(), ["planDigest"] = reviewedDigest,
            ["action"] = canPublish ? "publish" : "prepare", ["confirmation"] = canPublish ? "PUBLISH" : "PREPARE" };
        StudioApi.AtomicWrite(path, Encoding.UTF8.GetBytes(new JsonObject { ["key"] = key, ["body"] = body.DeepClone() }.ToJsonString()));
        // No automatic replay after an unknown POST outcome; the saved key is reconciled.
        JsonObject result;
        try { result = await api.Json($"/v1/studio/videos/{selectedVideo}/submit", body, key); }
        catch (StudioException e) when (e.SubmissionRejected) { File.Delete(path); reviewedDigest = ""; if (sendButton != null) sendButton.IsEnabled = false; throw; }
        catch { status.Text = "Request interrupted. Check saved submission before retrying; no new task was sent."; throw; }
        File.Delete(path);
        MessageBox.Show(result.ToJsonString(), T("Activity")); page = "Activity"; await Activity();
    }
    private async Task Web(string path, bool qualify = false, string? expectedTitle = null)
    {
        var viewer = new Window { Title = T("Studio editor"), Width = 1100, Height = 800, Owner = this };
        var web = new WebView2(); viewer.Content = web; viewers.Add(viewer);
        viewer.Closed += (_, _) => { web.Dispose(); viewers.Remove(viewer); }; viewer.Show();
        try {
            var environment = await CoreWebView2Environment.CreateAsync(null, api.ContextPath("webview"));
            await web.EnsureCoreWebView2Async(environment);
            web.CoreWebView2.Settings.AreDevToolsEnabled = false;
            web.CoreWebView2.Settings.AreDefaultContextMenusEnabled = false;
            web.CoreWebView2.Settings.IsPasswordAutosaveEnabled = false;
            web.CoreWebView2.Settings.IsGeneralAutofillEnabled = false;
            web.CoreWebView2.DownloadStarting += (_, args) => {
                try { StudioApi.SafeUrl(args.DownloadOperation.Uri); } catch (StudioException) { args.Cancel = true; return; }
                var save = new SaveFileDialog { FileName = Path.GetFileName(args.ResultFilePath), OverwritePrompt = true };
                if (save.ShowDialog(viewer) != true) { args.Cancel = true; return; }
                args.ResultFilePath = save.FileName; args.Handled = true;
            };
            web.CoreWebView2.NavigationStarting += (_, args) => { if (args.Uri.StartsWith("about:")) return; try { StudioApi.SafeUrl(args.Uri); } catch (StudioException) { args.Cancel = true; } };
            web.CoreWebView2.NewWindowRequested += (_, args) => { args.Handled = true; };
            foreach (var pair in api.CookieHeader.Split("; ", StringSplitOptions.RemoveEmptyEntries)) {
                var pieces = pair.Split('=', 2); var cookie = web.CoreWebView2.CookieManager.CreateCookie(pieces[0], pieces[1], StudioApi.Origin.Host, "/");
                cookie.IsSecure = true; cookie.IsHttpOnly = true; cookie.SameSite = CoreWebView2CookieSameSiteKind.Strict;
                cookie.Expires = api.Session!.Expires.UtcDateTime; web.CoreWebView2.CookieManager.AddOrUpdateCookie(cookie);
            }
            web.CoreWebView2.Navigate(StudioApi.SafeUrl(path).ToString());
            if (qualify) {
                var hydrated = false;
                for (var attempt = 0; attempt < 30; attempt++) {
                    await Task.Delay(1000);
                    var body = await web.CoreWebView2.ExecuteScriptAsync("document.body.innerText");
                    var text = System.Text.Json.JsonSerializer.Deserialize<string>(body) ?? "";
                    if (text.Contains("Edit & preview") && !text.Contains("Opening editor") &&
                        !string.IsNullOrEmpty(expectedTitle) && text.Contains(expectedTitle)) { hydrated = true; break; }
                }
                if (!hydrated) throw new StudioException("Advanced editor did not hydrate.");
                using var stream = File.Create(Path.Combine(StudioApi.StateRoot, "windows-editor.png"));
                await web.CoreWebView2.CapturePreviewAsync(CoreWebView2CapturePreviewImageFormat.Png, stream);
                viewer.Close();
            }
        } catch { viewer.Close(); throw; }
    }
}
