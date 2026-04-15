import { useCallback } from 'react';

/**
 * Hook to access Telegram WebApp native features.
 * Provides theme colors, MainButton, HapticFeedback, and other native capabilities.
 */
export function useTelegramNative() {
  const tg = window.Telegram?.WebApp;

  /**
   * Get theme parameter by key.
   * Falls back to default if not in Telegram or key doesn't exist.
   */
  const getThemeParam = useCallback(
    (key: string, fallback: string): string => {
      if (!tg?.themeParams) return fallback;
      return tg.themeParams[key] || fallback;
    },
    [tg]
  );

  /**
   * Get background color from Telegram theme.
   */
  const bgColor = useCallback(
    () => getThemeParam('bg_color', '#0f172a'),
    [getThemeParam]
  );

  /**
   * Get text color from Telegram theme.
   */
  const textColor = useCallback(
    () => getThemeParam('text_color', '#ffffff'),
    [getThemeParam]
  );

  /**
   * Get hint (secondary text) color from Telegram theme.
   */
  const hintColor = useCallback(
    () => getThemeParam('hint_color', '#9ca3af'),
    [getThemeParam]
  );

  /**
   * Get button color from Telegram theme.
   */
  const buttonColor = useCallback(
    () => getThemeParam('button_color', '#3b82f6'),
    [getThemeParam]
  );

  /**
   * Trigger haptic feedback (light impact).
   * Use for taps, clicks, and minor interactions.
   */
  const hapticLight = useCallback(() => {
    tg?.HapticFeedback?.impactOccurred('light');
  }, [tg]);

  /**
   * Trigger haptic feedback (medium impact).
   * Use for important actions like completing missions.
   */
  const hapticMedium = useCallback(() => {
    tg?.HapticFeedback?.impactOccurred('medium');
  }, [tg]);

  /**
   * Trigger haptic feedback (heavy impact).
   * Use for critical actions like territory capture.
   */
  const hapticHeavy = useCallback(() => {
    tg?.HapticFeedback?.impactOccurred('heavy');
  }, [tg]);

  /**
   * Trigger haptic notification feedback.
   * Use for alerts and notifications.
   */
  const hapticNotify = useCallback(
    (type: 'error' | 'success' | 'warning' = 'success') => {
      tg?.HapticFeedback?.notificationOccurred(type);
    },
    [tg]
  );

  /**
   * Trigger haptic selection change feedback.
   * Use for carousel/tab switching.
   */
  const hapticSelection = useCallback(() => {
    tg?.HapticFeedback?.selectionChanged();
  }, [tg]);

  /**
   * Show Telegram's MainButton with specified text.
   * Call with empty string to hide.
   */
  const setMainButton = useCallback(
    (text: string, onClick?: () => void, enabled = true) => {
      if (!tg?.MainButton) return;

      if (text) {
        tg.MainButton.setText(text);
        tg.MainButton.onClick(() => onClick?.());
        if (enabled) {
          tg.MainButton.enable();
          tg.MainButton.show();
        } else {
          tg.MainButton.disable();
          tg.MainButton.show();
        }
      } else {
        tg.MainButton.hide();
      }
    },
    [tg]
  );

  /**
   * Hide the MainButton.
   */
  const hideMainButton = useCallback(() => {
    tg?.MainButton?.hide();
  }, [tg]);

  /**
   * Expand the Telegram WebApp to full height.
   */
  const expand = useCallback(() => {
    tg?.expand();
  }, [tg]);

  /**
   * Close the Telegram WebApp.
   */
  const close = useCallback(() => {
    tg?.close();
  }, [tg]);

  /**
   * Enable vertical swipes to close the WebApp.
   */
  const enableSwipeClose = useCallback(() => {
    tg?.enableClosingConfirmation?.();
  }, [tg]);

  /**
   * Disable vertical swipes to close the WebApp.
   */
  const disableSwipeClose = useCallback(() => {
    tg?.disableClosingConfirmation?.();
  }, [tg]);

  return {
    isAvailable: !!tg,
    getThemeParam,
    bgColor,
    textColor,
    hintColor,
    buttonColor,
    hapticLight,
    hapticMedium,
    hapticHeavy,
    hapticNotify,
    hapticSelection,
    setMainButton,
    hideMainButton,
    expand,
    close,
    enableSwipeClose,
    disableSwipeClose,
  };
}
