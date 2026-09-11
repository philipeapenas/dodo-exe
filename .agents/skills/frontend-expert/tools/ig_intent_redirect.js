/**
 * IG Intent Auto-Redirect Tool
 * Saves the "zero-click" intent redirect logic for future projects.
 * Automatically triggers the native Instagram "Leave app / Open in Browser" modal.
 */
function triggerIGModal(fallbackUrl) {
    const userAgent = navigator.userAgent || navigator.vendor || window.opera;
    const isAndroid = /android/i.test(userAgent);
    
    // Convert relative fallbackUrl to Absolute URL for Android Intents
    const absoluteTarget = new URL(fallbackUrl, window.location.href).href;
    
    setTimeout(() => {
        if (isAndroid) {
            // Android: Chrome Intent forces the native IG modal or jumps straight to Chrome
            const noHttps = absoluteTarget.replace(/^https?:\/\//, '');
            window.location.href = `intent://${noHttps}#Intent;scheme=https;package=com.android.chrome;end;`;
        } else {
            // iOS: Direct fast-redirect intercepts the UI and triggers the native pop-up
            window.location.href = absoluteTarget;
        }
    }, 600); // 600ms delay ensures the trust-building UI paints before the modal locks the screen
}
