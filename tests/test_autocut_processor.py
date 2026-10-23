import subprocess

import pytest

from lazyedit.autocut_processor import AutocutProcessor


def processor(tmp_path, monkeypatch, results):
    source = tmp_path / "source.mp4"
    source.write_bytes(b"test")
    obj = AutocutProcessor(str(source), str(tmp_path), "source", ".mp4")
    monkeypatch.delenv("LAZYEDIT_WHISPER_CPU_MODEL", raising=False)
    monkeypatch.setattr(obj, "_select_gpu_model_candidates", lambda *_: (["large-v3", "medium"], None))
    calls = []

    def run(command, env):
        calls.append((command, dict(env)))
        return results.pop(0)

    monkeypatch.setattr(obj, "_run_logged_command", run)
    return obj, calls


@pytest.mark.parametrize("message", [
    "NVML_SUCCESS == DriverAPI::get()->nvmlInit_v2_() INTERNAL ASSERT FAILED",
    "Failed to initialize NVML: Driver/library version mismatch",
    "CUDA driver version is insufficient for CUDA runtime version",
])
def test_driver_failure_uses_one_cpu_attempt_not_smaller_gpu_models(tmp_path, monkeypatch, message):
    obj, calls = processor(tmp_path, monkeypatch, [(1, message), (0, "completed")])
    obj.run_autocut("mixed", 0)
    assert len(calls) == 2
    assert calls[0][1]["LAZYEDIT_WHISPER_DEVICE"] == "cuda"
    assert calls[1][1]["LAZYEDIT_WHISPER_DEVICE"] == "cpu"
    assert calls[1][1]["CUDA_VISIBLE_DEVICES"] == ""
    assert "--whisper-model medium" in calls[1][0]


def test_cpu_failure_surfaces_without_retry_loop(tmp_path, monkeypatch):
    obj, calls = processor(tmp_path, monkeypatch, [(1, "Failed to initialize NVML"), (1, "bad audio")])
    with pytest.raises(subprocess.CalledProcessError):
        obj.run_autocut("mixed", 0)
    assert len(calls) == 2


def test_unrelated_error_does_not_trigger_cpu_fallback(tmp_path, monkeypatch):
    obj, calls = processor(tmp_path, monkeypatch, [(1, "input file is corrupt")])
    with pytest.raises(subprocess.CalledProcessError):
        obj.run_autocut("mixed", 0)
    assert len(calls) == 1


def test_oom_still_uses_existing_smaller_gpu_model_path(tmp_path, monkeypatch):
    obj, calls = processor(tmp_path, monkeypatch, [(1, "CUDA out of memory"), (0, "completed")])
    obj.run_autocut("mixed", 0)
    assert len(calls) == 2
    assert all(env["LAZYEDIT_WHISPER_DEVICE"] == "cuda" for _, env in calls)


def test_nonfatal_nvml_warning_keeps_successful_gpu_result(tmp_path, monkeypatch):
    obj, calls = processor(tmp_path, monkeypatch, [(0, "UserWarning: Can't initialize NVML\ncompleted")])
    obj.run_autocut("mixed", 0)
    assert len(calls) == 1
