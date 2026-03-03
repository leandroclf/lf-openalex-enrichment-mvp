import os
import unittest

from backend.src.service import load_openalex_runtime_config, run_openalex_with_retry


class TestIssue001RuntimeRetry(unittest.TestCase):
    def setUp(self):
        self._old_env = dict(os.environ)

    def tearDown(self):
        os.environ.clear()
        os.environ.update(self._old_env)

    def test_load_openalex_runtime_config_defaults(self):
        os.environ.pop("OPENALEX_TIMEOUT", None)
        os.environ.pop("OPENALEX_MAX_RETRIES", None)
        os.environ.pop("OPENALEX_RETRY_BACKOFF_SECONDS", None)

        cfg = load_openalex_runtime_config()
        self.assertEqual(cfg["timeout_seconds"], 12.0)
        self.assertEqual(cfg["max_retries"], 2)
        self.assertEqual(cfg["backoff_seconds"], 0.5)

    def test_load_openalex_runtime_config_env_override(self):
        os.environ["OPENALEX_TIMEOUT"] = "30"
        os.environ["OPENALEX_MAX_RETRIES"] = "4"
        os.environ["OPENALEX_RETRY_BACKOFF_SECONDS"] = "0.2"

        cfg = load_openalex_runtime_config()
        self.assertEqual(cfg["timeout_seconds"], 30.0)
        self.assertEqual(cfg["max_retries"], 4)
        self.assertEqual(cfg["backoff_seconds"], 0.2)

    def test_run_openalex_with_retry_succeeds_after_transient_failure(self):
        attempts = {"n": 0}

        def fake_call(timeout=None):
            attempts["n"] += 1
            if attempts["n"] < 3:
                raise TimeoutError("temporary timeout")
            return {"ok": True, "timeout": timeout}

        out = run_openalex_with_retry(
            fake_call,
            timeout_seconds=9.0,
            max_retries=3,
            backoff_seconds=0.0,
            sleep_fn=lambda _: None,
        )
        self.assertTrue(out["ok"])
        self.assertEqual(out["timeout"], 9.0)
        self.assertEqual(attempts["n"], 3)

    def test_run_openalex_with_retry_exhausts_and_raises(self):
        attempts = {"n": 0}

        def always_timeout(timeout=None):
            attempts["n"] += 1
            raise TimeoutError("still failing")

        with self.assertRaises(TimeoutError):
            run_openalex_with_retry(
                always_timeout,
                timeout_seconds=5.0,
                max_retries=2,
                backoff_seconds=0.0,
                sleep_fn=lambda _: None,
            )

        self.assertEqual(attempts["n"], 3)

    def test_run_openalex_with_retry_does_not_retry_non_transient_error(self):
        attempts = {"n": 0}

        def fatal_call(timeout=None):
            attempts["n"] += 1
            raise ValueError("bad payload")

        with self.assertRaises(ValueError):
            run_openalex_with_retry(
                fatal_call,
                timeout_seconds=5.0,
                max_retries=3,
                backoff_seconds=0.0,
                sleep_fn=lambda _: None,
            )

        self.assertEqual(attempts["n"], 1)


if __name__ == "__main__":
    unittest.main()
