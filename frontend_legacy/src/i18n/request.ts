import { getRequestConfig } from 'next-intl/server';
import { notFound } from 'next/navigation';

// Supported locales
const locales = ['en', 'ar'] as const;
type Locale = (typeof locales)[number];

export default getRequestConfig(async ({ requestLocale }) => {
    // Wait for the locale to be determined (may be undefined during static generation)
    let locale = await requestLocale;

    // Fallback to 'en' if locale is undefined (static generation)
    if (!locale) {
        locale = 'en';
    }

    // Validate that the incoming `locale` parameter is valid
    if (!locales.includes(locale as Locale)) {
        notFound();
    }

    return {
        locale,
        messages: (await import(`../../messages/${locale}.json`)).default
    };
});
