"""Exercise the actual pure readiness functions without loading GPU models."""
import ast
from pathlib import Path


def readiness_functions():
    source = Path(__file__).resolve().parents[1] / "app.py"
    tree = ast.parse(source.read_text())
    names = {"_ready_for_publish_with_options", "_publish_requires_processing"}
    namespace = {"_logo_overlay_enabled": lambda logo: bool(logo.get("enabled")),
                 "is_portrait_blurfill_enabled": lambda fill: bool((fill or {}).get("enabled"))}
    selected = ast.Module(body=[node for node in tree.body
        if isinstance(node, ast.FunctionDef) and node.name in names], type_ignores=[])
    exec(compile(selected, str(source), "exec"), namespace)
    return namespace["_publish_requires_processing"]


def test_finished_outputs_are_reusable_but_new_context_or_missing_render_needs_work():
    requires = readiness_functions()
    status = {"steps": {name: {"status": "done"} for name in
        ["transcribe", "translate", "keyframes", "metadata_zh", "metadata_en", "cover", "burn"]}}
    assert not requires(status, {}, {"enabled": True})
    assert requires(status, {"autoCorrectSubtitles": True, "autoCorrectPrompt": "context"}, {})
    assert requires(status, {"metadataPrompt": "new context"}, {})
    assert not requires(status, {"metadataPrompt": "context", "useCorrectionPromptForMetadata": False}, {})
    status["steps"]["burn"]["status"] = "skipped"
    assert requires(status, {"burnSubtitles": False}, {"enabled": True})
    assert not requires(status, {"burnSubtitles": False}, {"enabled": False})
    assert requires(status, {"burnSubtitles": False, "burnLayout": {"portraitBlurFill": {"enabled": True}}}, {})
