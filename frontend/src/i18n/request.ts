import { getRequestConfig } from 'next-intl/server';
import { requestLocale } from 'next-intl/server';

export default getRequestConfig(async () => {
    // Use the new requestLocale API instead of deprecated locale parameter
    const locale = await requestLocale();
    const safeLocale = locale ?? 'en';

    return {
        messages: (await import(`../../messages/${safeLocale}.json`)).default
    };
});
