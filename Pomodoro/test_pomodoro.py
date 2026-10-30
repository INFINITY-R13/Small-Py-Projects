"""
Unit tests for the Pomodoro Timer application.
Runs headless (Tk window withdrawn) without external dependencies.
"""

import time
import unittest
import tkinter as tk
from unittest.mock import patch
from pomodoro import PomodoroApp, DEFAULT_DURATIONS


class TestFormattingAndLabels(unittest.TestCase):
    def test_format_time_standard(self):
        self.assertEqual(PomodoroApp._format_time(0), "00:00")
        self.assertEqual(PomodoroApp._format_time(5), "00:05")
        self.assertEqual(PomodoroApp._format_time(59), "00:59")
        self.assertEqual(PomodoroApp._format_time(60), "01:00")
        self.assertEqual(PomodoroApp._format_time(1500), "25:00")
        self.assertEqual(PomodoroApp._format_time(3599), "59:59")

    def test_format_time_negative(self):
        self.assertEqual(PomodoroApp._format_time(-1), "00:00")
        self.assertEqual(PomodoroApp._format_time(-100), "00:00")

    def test_format_time_float_ceiling(self):
        # 1499.1 seconds left should still display as 25:00
        self.assertEqual(PomodoroApp._format_time(1499.1), "25:00")
        self.assertEqual(PomodoroApp._format_time(1498.9), "24:59")
        self.assertEqual(PomodoroApp._format_time(0.2), "00:01")

    def test_mode_labels(self):
        self.assertEqual(PomodoroApp._mode_label("pomodoro"), "Focus Time")
        self.assertEqual(PomodoroApp._mode_label("short_break"), "Short Break")
        self.assertEqual(PomodoroApp._mode_label("long_break"), "Long Break")
        self.assertEqual(PomodoroApp._mode_label("other"), "other")


class TestPomodoroAppLifecycle(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        try:
            cls.app = PomodoroApp()
            cls.app.withdraw()
        except tk.TclError:
            raise unittest.SkipTest("Tkinter display not available in this environment")

    @classmethod
    def tearDownClass(cls):
        if hasattr(cls, "app") and cls.app:
            cls.app.on_close()

    def setUp(self):
        self.app.switch_mode("pomodoro", force=True)
        self.app.sessions_done = 0
        self.app.daily_goal.set(4)
        self.app.auto_start.set(False)
        self.app.durations = dict(DEFAULT_DURATIONS)
        self.app.reset_timer()

    def test_initial_state(self):
        self.assertEqual(self.app.mode.get(), "pomodoro")
        self.assertFalse(self.app.running)
        self.assertEqual(self.app.total, 1500.0)
        self.assertEqual(self.app.remaining, 1500.0)
        self.assertEqual(self.app.sessions_done, 0)
        self.assertEqual(self.app.daily_goal.get(), 4)
        self.assertFalse(self.app.auto_start.get())
        self.assertEqual(self.app._get_start_label(), "Start")

    def test_start_pause_resume_reset(self):
        # Start
        self.app.start_pause()
        self.assertTrue(self.app.running)
        self.assertIsNotNone(self.app.end_time)
        self.assertEqual(self.app._get_start_label(), "Pause")

        # Simulate elapsed time
        self.app.remaining = 1450.0
        self.app.end_time = time.monotonic() + 1450.0

        # Pause
        self.app.start_pause()
        self.assertFalse(self.app.running)
        self.assertEqual(self.app._get_start_label(), "Resume")
        self.assertAlmostEqual(self.app.remaining, 1450.0, delta=0.5)

        # Resume
        self.app.start_pause()
        self.assertTrue(self.app.running)
        self.assertEqual(self.app._get_start_label(), "Pause")

        # Reset
        self.app.reset_timer()
        self.assertFalse(self.app.running)
        self.assertEqual(self.app.remaining, 1500.0)
        self.assertEqual(self.app._get_start_label(), "Start")

    def test_mode_switching(self):
        # Switch to Short Break
        self.app.switch_mode("short_break")
        self.assertEqual(self.app.mode.get(), "short_break")
        self.assertEqual(self.app.total, 300.0)
        self.assertEqual(self.app.remaining, 300.0)
        self.assertFalse(self.app.running)

        # Switch to Long Break
        self.app.switch_mode("long_break")
        self.assertEqual(self.app.mode.get(), "long_break")
        self.assertEqual(self.app.total, 900.0)
        self.assertEqual(self.app.remaining, 900.0)

        # Clicking active mode without force does not reset progress
        self.app.remaining = 400.0
        self.app.switch_mode("long_break", force=False)
        self.assertEqual(self.app.remaining, 400.0)

        # Force switch resets
        self.app.switch_mode("long_break", force=True)
        self.assertEqual(self.app.remaining, 900.0)

    @patch.object(PomodoroApp, "play_notification_sound")
    def test_session_complete_progression(self, mock_sound):
        # 1st Pomodoro completes -> transitions to short_break
        self.app.switch_mode("pomodoro", force=True)
        self.app.session_complete()
        self.assertEqual(self.app.sessions_done, 1)
        self.assertEqual(self.app.mode.get(), "short_break")
        self.assertEqual(self.app.remaining, 300.0)
        self.assertFalse(self.app.running)
        self.assertEqual(self.app._get_start_label(), "Start")

        # Short break completes -> transitions to pomodoro (sessions_done unchanged)
        self.app.session_complete()
        self.assertEqual(self.app.sessions_done, 1)
        self.assertEqual(self.app.mode.get(), "pomodoro")
        self.assertEqual(self.app.remaining, 1500.0)

        # Complete 2nd and 3rd Pomodoros
        self.app.session_complete()  # Pomodoro 2 -> short_break
        self.assertEqual(self.app.sessions_done, 2)
        self.assertEqual(self.app.mode.get(), "short_break")

        self.app.session_complete()  # Break 2 -> pomodoro
        self.assertEqual(self.app.mode.get(), "pomodoro")

        self.app.session_complete()  # Pomodoro 3 -> short_break
        self.assertEqual(self.app.sessions_done, 3)
        self.assertEqual(self.app.mode.get(), "short_break")

        self.app.session_complete()  # Break 3 -> pomodoro
        self.assertEqual(self.app.mode.get(), "pomodoro")

        # 4th Pomodoro completes -> transitions to long_break!
        self.app.session_complete()
        self.assertEqual(self.app.sessions_done, 4)
        self.assertEqual(self.app.mode.get(), "long_break")
        self.assertEqual(self.app.remaining, 900.0)
        self.assertEqual(mock_sound.call_count, 7)

    @patch.object(PomodoroApp, "play_notification_sound")
    def test_auto_start_transition(self, mock_sound):
        self.app.auto_start.set(True)
        self.app.switch_mode("pomodoro", force=True)
        self.app.session_complete()
        # Should have automatically switched to short_break AND started
        self.assertEqual(self.app.mode.get(), "short_break")
        self.assertTrue(self.app.running)
        self.assertEqual(self.app._get_start_label(), "Pause")
        self.app.start_pause()  # pause to cancel scheduled callback

    def test_rebuild_dots_scaling(self):
        # Default goal (4)
        self.app.daily_goal.set(4)
        self.app.sessions_done = 2
        self.app._rebuild_dots()
        self.assertTrue(len(self.app.dots_frame.winfo_children()) > 0)

        # Maximum goal (20) to ensure dynamic scaling works without error
        self.app.daily_goal.set(20)
        self.app.sessions_done = 15
        self.app._rebuild_dots()
        self.assertTrue(len(self.app.dots_frame.winfo_children()) > 0)

    def test_settings_modal_singleton(self):
        self.app.open_settings()
        first_win = self.app.settings_win
        self.assertIsNotNone(first_win)
        self.assertTrue(first_win.winfo_exists())

        # Opening again should reuse existing modal
        self.app.open_settings()
        self.assertEqual(self.app.settings_win, first_win)

        first_win.destroy()
        self.app.update_idletasks()
        self.assertIsNone(self.app.settings_win)


if __name__ == "__main__":
    unittest.main()
