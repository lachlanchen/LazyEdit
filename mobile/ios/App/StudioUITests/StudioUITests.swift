import XCTest

final class StudioUITests: XCTestCase {
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
            let password = app.secureTextFields["studio.password"]
            password.tap(); password.typeText(try XCTUnwrap(credentials["password"]))
            app.buttons["studio.signIn"].tap()
        }
        XCTAssertTrue(app.navigationBars["Your Studio"].waitForExistence(timeout: 60))
        capture("Native library", app)
        for label in ["Activity", "Account", "Upload", "Studio"] {
            tapTab(label, app)
            XCTAssertTrue(app.navigationBars[label == "Studio" ? "Your Studio" : label].waitForExistence(timeout: 10))
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
        XCTAssertTrue(app.buttons["Edit & publish"].waitForExistence(timeout: 10))
        app.buttons["Preview video"].tap()
        capture("Native preview", app)
        app.buttons["Edit & publish"].tap()
        XCTAssertTrue(app.navigationBars["Studio editor"].waitForExistence(timeout: 10))
        XCTAssertTrue(app.webViews.firstMatch.waitForExistence(timeout: 30))
        XCTAssertTrue(app.webViews.staticTexts["AutoPublish pipeline"].waitForExistence(timeout: 90), app.debugDescription)
        capture("Existing editor", app)
        app.navigationBars["Studio editor"].buttons["Done"].tap()
        XCTAssertTrue(app.buttons["Edit & publish"].waitForExistence(timeout: 10))
        // No processing/publication buttons are ever pressed in this smoke test.
    }
    @MainActor
    private func tapTab(_ label: String, _ app: XCUIApplication) {
        let button = app.tabBars.buttons[label]
        XCTAssertTrue(button.waitForExistence(timeout: 10))
        // Simulator accessibility may supply an invalid suggested hit point
        // for a Liquid Glass tab; the observed element frame remains correct.
        button.coordinate(withNormalizedOffset: CGVector(dx: 0.5, dy: 0.5)).tap()
    }
    @MainActor
    private func capture(_ name: String, _ app: XCUIApplication) {
        let attachment = XCTAttachment(screenshot: app.screenshot())
        attachment.name = name; attachment.lifetime = .keepAlways
        add(attachment)
    }
}
