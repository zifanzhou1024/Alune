import unittest
from unittest.mock import AsyncMock
from unittest.mock import Mock
from unittest.mock import patch

from adb_shell.exceptions import AdbTimeoutError
import cv2
import numpy as np

from alune.adb import ADB
from alune.images import Button
from alune.images import Image
from alune.tft.app import GameState
from alune.tft.app import GameStateImageResult
from alune.tft.app import TFTApp


class ClientControlsTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.adb = Mock()
        self.adb.click_button = AsyncMock()
        self.adb.get_screen = AsyncMock(return_value=object())
        self.config = Mock()
        self.config.get_game_mode.return_value = "normal"
        with patch.object(TFTApp, "setup_hotkeys"):
            self.app = TFTApp(self.adb, self.config)

    async def test_click_sends_tap_instead_of_ignored_swipe(self):
        adb = ADB.__new__(ADB)
        adb._wrap_shell_call = AsyncMock()
        await adb.click(1060, 631)
        adb._wrap_shell_call.assert_awaited_once_with("input tap 1060 631")

    async def test_launch_resolves_current_android_activity(self):
        adb = ADB.__new__(ADB)
        adb.tft_package_name = "com.riotgames.league.teamfighttactics"
        adb._tft_activity_name = "old.Activity"
        component = adb.tft_package_name + "/com.epicgames.unreal.SplashActivity"
        adb._wrap_shell_call = AsyncMock(side_effect=["priority=0\n" + component + "\n", "Starting: Intent"])
        await adb.start_tft_app()
        self.assertEqual(adb._wrap_shell_call.await_args.args, ("am start -n " + component,))

    async def test_capture_retries_empty_frame(self):
        adb = ADB.__new__(ADB)
        expected = np.zeros((8, 8), dtype=np.uint8)
        _, png = cv2.imencode(".png", expected)
        adb._device = Mock(exec_out=AsyncMock(side_effect=[b"", png.tobytes()]))
        with patch("alune.adb.asyncio.sleep", new_callable=AsyncMock):
            result = await adb._get_screen_capture()
        np.testing.assert_array_equal(result, expected)

    async def test_invalid_capture_enters_disconnect_recovery(self):
        adb = ADB.__new__(ADB)
        adb._device = Mock(exec_out=AsyncMock(return_value=b"invalid PNG"))
        with patch("alune.adb.asyncio.sleep", new_callable=AsyncMock):
            with self.assertRaises(AdbTimeoutError):
                await adb._get_screen_capture()
        self.assertEqual(adb._device.exec_out.await_count, 3)

    async def test_current_start_requires_normal_lobby_heading(self):
        with patch("alune.tft.app.screen.get_button_on_screen", side_effect=lambda _, b: b is Button.start):
            with patch("alune.tft.app.screen.get_on_screen", return_value=None):
                self.assertFalse(self.app._is_lobby(None))
            with patch("alune.tft.app.screen.get_on_screen", side_effect=lambda _, p: p == Image.NORMAL_LOBBY):
                self.assertTrue(self.app._is_lobby(None))

    async def test_existing_queue_resumes_accept_wait(self):
        self.app.queue = AsyncMock()
        await self.app.take_app_decision(GameStateImageResult(GameState.IN_QUEUE))
        self.app.queue.assert_awaited_once()
        self.adb.click_button.assert_not_awaited()

    async def test_timeout_uses_current_cancel_position(self):
        with patch(
            "alune.tft.app.screen.get_button_on_screen", side_effect=lambda _, b: b is Button.cancel_queue_current
        ):
            await self.app.exit_queue_if_active()
        self.adb.click_button.assert_awaited_once_with(Button.cancel_queue_current)

    async def test_timeout_does_not_click_after_queue_disappears(self):
        with (
            patch("alune.tft.app.screen.get_button_on_screen", return_value=None),
            patch("alune.tft.app.screen.get_on_screen", return_value=None),
        ):
            await self.app.exit_queue_if_active()
        self.adb.click_button.assert_not_awaited()


if __name__ == "__main__":
    unittest.main()
