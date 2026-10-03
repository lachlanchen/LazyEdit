import XCTest

final class StudioUITests: XCTestCase {
    @MainActor
    func testMemberPrivateLibraryAndLoginDesktop() throws {
        continueAfterFailure = false
        let path = ProcessInfo.processInfo.environment["STUDIO_TEST_CREDENTIALS"] ?? ""
        guard !path.isEmpty else { throw XCTSkip("Set private STUDIO_TEST_CREDENTIALS.") }
        let credentials = try XCTUnwrap(JSONSerialization.jsonObject(with: Data(contentsOf: URL(fileURLWithPath: path))) as? [String: String])
        addUIInterruptionMonitor(withDescription: "Private QA password prompt") { alert in
            if alert.buttons["Not Now"].exists { alert.buttons["Not Now"].tap(); return true }
            return false
        }
        let app = XCUIApplication(); app.launch()
        // System AutoFill can outlive a previous QA run. Do not save the
        // reviewer password or let that overlay intercept native tab taps.
        let notNow = XCUIApplication(bundleIdentifier: "com.apple.springboard").buttons["Not Now"]
        if notNow.waitForExistence(timeout: 3) { notNow.tap() }
        // A prior administrator QA session can survive in the simulator's
        // Keychain. Explicitly sign it out before qualifying member isolation.
        if !app.secureTextFields["studio.password"].waitForExistence(timeout: 5) {
            tapTab("Account", app)
            let signOut = app.buttons["Sign out"]; scrollTo(signOut, app); signOut.tap()
            try XCTUnwrap(app.buttons.matching(identifier: "Sign out").allElementsBoundByIndex.first(where: { $0.isHittable })).coordinate(withNormalizedOffset: CGVector(dx: 0.5, dy: 0.5)).tap()
            XCTAssertTrue(app.secureTextFields["studio.password"].waitForExistence(timeout: 30))
        }
        if app.secureTextFields["studio.password"].waitForExistence(timeout: 5) {
            replaceText(app.textFields["studio.username"], with: try XCTUnwrap(credentials["username"]))
            replaceText(app.secureTextFields["studio.password"], with: try XCTUnwrap(credentials["password"]))
            app.buttons["studio.signIn"].tap()
            if notNow.waitForExistence(timeout: 5) { notNow.tap() }
        }
        XCTAssertTrue(app.tabBars.buttons["Studio"].waitForExistence(timeout: 60))
        tapTab("Studio", app)
        XCTAssertTrue(app.navigationBars["Your Studio"].waitForExistence(timeout: 30))
        capture("Invited member demo library", app)
        tapTab("Account", app)
        XCTAssertTrue(app.staticTexts["Private Docker workspace"].waitForExistence(timeout: 30))
        XCTAssertTrue(app.buttons["Platform accounts"].waitForExistence(timeout: 30))
        XCTAssertTrue(app.buttons["Delete account"].waitForExistence(timeout: 30))
        XCTAssertFalse(app.buttons["Create invitation"].exists)
        XCTAssertFalse(app.buttons["Switch to existing Pi workspace"].exists)
        capture("Invited member account controls", app)
        app.buttons["Platform accounts"].tap()
        XCTAssertTrue(app.webViews.firstMatch.waitForExistence(timeout: 30))
        XCTAssertTrue(app.webViews.buttons["Shipinhao"].waitForExistence(timeout: 60), "Login module is ready, not merely static HTML")
        XCTAssertTrue(app.webViews.buttons["Keep QR visible"].waitForExistence(timeout: 60))
        let finished = XCTNSPredicateExpectation(predicate: NSPredicate(format: "exists == false"), object: app.staticTexts["Opening editor…"])
        XCTAssertEqual(XCTWaiter.wait(for: [finished], timeout: 20), .completed)
        app.webViews.buttons["Shipinhao"].tap()
        XCTAssertTrue(app.webViews.staticTexts["Connected. Sign in using the private browser below."].waitForExistence(timeout: 60))
        app.webViews.buttons["Keep QR visible"].tap()
        XCTAssertTrue(app.webViews.staticTexts["QR image kept visible. Tap the image to enlarge a QR area; tap again to restore. No live traffic. Reconnect to refresh."].waitForExistence(timeout: 10))
        capture("Mobile platform login controls", app)
        app.webViews.buttons["Close platform browser"].tap()
        XCTAssertTrue(app.webViews.staticTexts["Browser closed. Your login is saved; choose a platform to reopen it."].waitForExistence(timeout: 15))
        app.navigationBars["Studio editor"].buttons["Done"].tap()
        let signOut = app.buttons["Sign out"]; scrollTo(signOut, app); signOut.tap()
        try XCTUnwrap(app.buttons.matching(identifier: "Sign out").allElementsBoundByIndex.first(where: { $0.isHittable })).coordinate(withNormalizedOffset: CGVector(dx: 0.5, dy: 0.5)).tap()
        XCTAssertTrue(app.secureTextFields["studio.password"].waitForExistence(timeout: 30))
        app.terminate()
    }
    @MainActor
    func testMacNativeAccount() throws {
        continueAfterFailure = false
        let path = ProcessInfo.processInfo.environment["STUDIO_TEST_CREDENTIALS"] ?? ""
        guard !path.isEmpty else { throw XCTSkip("Set private STUDIO_TEST_CREDENTIALS.") }
        let credentials = try XCTUnwrap(JSONSerialization.jsonObject(with: Data(contentsOf: URL(fileURLWithPath: path))) as? [String: String])
        let app = XCUIApplication(); app.launch()
        if app.secureTextFields["studio.password"].waitForExistence(timeout: 5) {
            app.textFields["studio.username"].tap()
            app.textFields["studio.username"].typeText(try XCTUnwrap(credentials["username"]))
            app.secureTextFields["studio.password"].tap()
            app.secureTextFields["studio.password"].typeText(try XCTUnwrap(credentials["password"]))
            app.buttons["studio.signIn"].tap()
        }
        XCTAssertTrue(app.staticTexts["Your Studio"].waitForExistence(timeout: 60) || app.navigationBars["Your Studio"].exists)
        capture("Native Mac library", app)
        app.terminate(); app.launch()
        XCTAssertFalse(app.secureTextFields["studio.password"].waitForExistence(timeout: 5), "Native session survives relaunch")
        capture("Native Mac persisted session", app)
    }
    @MainActor
    func testAdministratorInvitesAndWorkspaceSwitch() throws {
        continueAfterFailure = false
        let path = ProcessInfo.processInfo.environment["STUDIO_TEST_CREDENTIALS"] ?? ""
        guard !path.isEmpty else { throw XCTSkip("Set private STUDIO_TEST_CREDENTIALS.") }
        let credentials = try XCTUnwrap(JSONSerialization.jsonObject(with: Data(contentsOf: URL(fileURLWithPath: path))) as? [String: String])
        let app = XCUIApplication(); app.launch()
        if app.secureTextFields["studio.password"].waitForExistence(timeout: 5) {
            let username = app.textFields["studio.username"]
            username.tap(); username.typeText(try XCTUnwrap(credentials["username"]))
            app.secureTextFields["studio.password"].tap(); app.secureTextFields["studio.password"].typeText(try XCTUnwrap(credentials["password"]))
            app.buttons["studio.signIn"].tap()
        }
        XCTAssertTrue(app.navigationBars["Your Studio"].waitForExistence(timeout: 60))
        tapTab("Account", app)
        XCTAssertTrue(app.buttons["Create invitation"].waitForExistence(timeout: 30))
        app.buttons["Create invitation"].tap()
        XCTAssertTrue(app.buttons["Share invitation"].waitForExistence(timeout: 30))
        let docker = app.buttons["Switch to private Docker workspace"]
        scrollTo(docker, app); docker.tap()
        XCTAssertTrue(app.staticTexts["Private Docker workspace"].waitForExistence(timeout: 240))
        XCTAssertTrue(app.buttons["Platform accounts"].exists)
        capture("Native private workspace", app)
        let owner = app.buttons["Switch to existing Pi workspace"]
        scrollTo(owner, app); owner.tap()
        XCTAssertTrue(app.staticTexts["Existing Pi workspace"].waitForExistence(timeout: 60))
        capture("Native administrator Pi workspace", app)
    }
    @MainActor
    func testOwnerNavigationAndUpload() throws {
        continueAfterFailure = false
        // Credentials remain in the simulator host's private configuration.
        // Run only on the dedicated LazyEdit simulator, never a personal device.
        let path = ProcessInfo.processInfo.environment["STUDIO_TEST_CREDENTIALS"] ?? ""
        guard !path.isEmpty else { throw XCTSkip("Set private STUDIO_TEST_CREDENTIALS in the test runner environment.") }
        let data = try Data(contentsOf: URL(fileURLWithPath: path))
        let credentials = try XCTUnwrap(JSONSerialization.jsonObject(with: data) as? [String: String])
        let app = XCUIApplication()
        app.launch()
        if app.secureTextFields["studio.password"].waitForExistence(timeout: 5) {
            let username = app.textFields["studio.username"]
            username.tap(); username.typeText(try XCTUnwrap(credentials["username"]))
            let password = app.secureTextFields["studio.password"]
            password.tap(); password.typeText(try XCTUnwrap(credentials["password"]))
            app.buttons["studio.signIn"].tap()
        }
        XCTAssertTrue(app.navigationBars["Your Studio"].waitForExistence(timeout: 60))
        capture("Native library", app)
        for label in ["Activity", "Account", "Upload", "Studio"] {
            tapTab(label, app)
            XCTAssertTrue(app.navigationBars[label == "Studio" ? "Your Studio" : label].waitForExistence(timeout: 10), app.debugDescription)
        }
        app.terminate(); app.launch()
        XCTAssertTrue(app.navigationBars["Your Studio"].waitForExistence(timeout: 20), "Keychain session survives relaunch")
        tapTab("Upload", app)
        capture("Native upload", app)
        app.buttons["Photos"].tap()
        let clip = app.images.matching(NSPredicate(format: "label BEGINSWITH %@", "Video, three seconds")).firstMatch
        XCTAssertTrue(clip.waitForExistence(timeout: 30), app.debugDescription)
        clip.coordinate(withNormalizedOffset: CGVector(dx: 0.5, dy: 0.5)).tap()
        XCTAssertTrue(app.buttons["studio.upload"].waitForExistence(timeout: 30), app.debugDescription)
        // Persist the staged copy through an actual process restart.
        app.terminate(); app.launch()
        XCTAssertTrue(app.navigationBars["Your Studio"].waitForExistence(timeout: 20))
        tapTab("Upload", app)
        XCTAssertTrue(app.buttons["studio.upload"].waitForExistence(timeout: 20))
        app.buttons["studio.upload"].tap()
        XCTAssertTrue(app.buttons["Open video"].waitForExistence(timeout: 180), app.debugDescription)
        capture("Uploaded video", app)
        app.buttons["Open video"].tap()
        XCTAssertTrue(app.buttons["studio.compose"].waitForExistence(timeout: 10))
        app.buttons["Preview video"].tap()
        capture("Native preview", app)
        app.buttons["studio.compose"].tap()
        XCTAssertTrue(app.navigationBars["Prepare & publish"].waitForExistence(timeout: 10))
        let context = app.textViews["studio.context"]
        XCTAssertTrue(context.waitForExistence(timeout: 60), app.debugDescription)
        context.tap(); context.typeText("Native UI regression fixture: a plain green video, no dialogue.")
        if app.buttons["Hide keyboard"].waitForExistence(timeout: 3) { app.buttons["Hide keyboard"].tap() }
        scrollTo(app.buttons["studio.reviewChoices"], app)
        capture("Native publish choices", app)
        app.buttons["studio.reviewChoices"].tap()
        XCTAssertTrue(app.navigationBars["Review choices"].waitForExistence(timeout: 60), app.debugDescription)
        capture("Native review layout", app)
        app.navigationBars["Review choices"].buttons["Done"].tap()
        app.navigationBars["Prepare & publish"].buttons["Done"].tap()
        app.buttons["studio.compose"].tap()
        XCTAssertTrue(context.waitForExistence(timeout: 30))
        XCTAssertTrue((context.value as? String ?? "").contains("Native UI regression"), "Video choices persist")
        app.navigationBars["Prepare & publish"].buttons["Done"].tap()
        app.buttons["Full editor · subtitles, metadata & cover"].tap()
        XCTAssertTrue(app.navigationBars["Studio editor"].waitForExistence(timeout: 10))
        XCTAssertTrue(app.webViews.firstMatch.waitForExistence(timeout: 30))
        XCTAssertTrue(app.webViews.staticTexts["AutoPublish pipeline"].waitForExistence(timeout: 90), app.debugDescription)
        capture("Existing editor", app)
        app.navigationBars["Studio editor"].buttons["Done"].tap()
        XCTAssertTrue(app.buttons["studio.compose"].waitForExistence(timeout: 10))
        tapTab("Studio", app)
        XCTAssertTrue(app.navigationBars["Your Studio"].waitForExistence(timeout: 10))
        let row = app.cells.containing(.staticText, identifier: "native-studio-smoke.mp4").firstMatch
        XCTAssertTrue(row.waitForExistence(timeout: 20), app.debugDescription)
        row.swipeLeft()
        app.buttons["Remove"].tap()
        app.buttons["Removed videos"].tap()
        XCTAssertTrue(app.navigationBars["Removed videos"].waitForExistence(timeout: 10))
        let removed = app.cells.containing(.staticText, identifier: "native-studio-smoke.mp4").firstMatch
        XCTAssertTrue(removed.waitForExistence(timeout: 30), app.debugDescription)
        removed.buttons["Restore"].tap()
        capture("Reversible library removal", app)
        app.navigationBars["Removed videos"].buttons["Done"].tap()
        XCTAssertTrue(row.waitForExistence(timeout: 30))
        // No processing/publication buttons are ever pressed in this smoke test.
    }
    @MainActor
    private func scrollTo(_ element: XCUIElement, _ app: XCUIApplication) {
        for _ in 0..<10 {
            if element.exists && element.isHittable { return }
            let form = app.collectionViews.firstMatch
            form.coordinate(withNormalizedOffset: CGVector(dx: 0.97, dy: 0.85))
                .press(forDuration: 0.1, thenDragTo: form.coordinate(withNormalizedOffset: CGVector(dx: 0.97, dy: 0.2)))
        }
        XCTAssertTrue(element.isHittable, app.debugDescription)
    }
    @MainActor
    private func replaceText(_ field: XCUIElement, with text: String) {
        field.tap()
        if let existing = field.value as? String, existing != field.placeholderValue {
            field.typeText(String(repeating: XCUIKeyboardKey.delete.rawValue, count: min(existing.count, 256)))
        }
        field.typeText(text)
    }
    @MainActor
    private func tapTab(_ label: String, _ app: XCUIApplication) {
        let button = app.tabBars.buttons[label]
        XCTAssertTrue(button.waitForExistence(timeout: 10))
        // Liquid Glass simulator tabs sometimes report {-1, -1} for the
        // suggested hit point. The observed accessibility frame is usable.
        button.coordinate(withNormalizedOffset: CGVector(dx: 0.5, dy: 0.5)).tap()
        let selected = XCTNSPredicateExpectation(predicate: NSPredicate(format: "selected == true"), object: button)
        XCTAssertEqual(XCTWaiter.wait(for: [selected], timeout: 10), .completed, "Requested native tab is selected")
    }
    @MainActor
    private func capture(_ name: String, _ app: XCUIApplication) {
        let attachment = XCTAttachment(screenshot: app.screenshot())
        attachment.name = name; attachment.lifetime = .keepAlways
        add(attachment)
    }
}
