"use client";
import { useLocale } from 'next-intl';
import { useRouter, usePathname } from 'next/navigation';
import { Globe } from 'lucide-react';

export default function LocaleSwitcher() {
    const locale = useLocale();
    const router = useRouter();
    const pathname = usePathname();

    const handleLocaleChange = (newLocale: string) => {
        // Current path e.g., /en/dashboard
        // We want to replace the first segment
        const segments = pathname.split('/');
        segments[1] = newLocale;
        const newPath = segments.join('/');
        router.replace(newPath);
    };

    return (
        <div className="flex justify-center p-4">
            <button
                onClick={() => handleLocaleChange(locale === 'ar' ? 'en' : 'ar')}
                className="flex items-center gap-2 text-sm px-4 py-2 bg-gray-900/50 hover:bg-gray-800 rounded-lg border border-gray-700 transition-colors"
            >
                <Globe size={16} />
                {locale === 'ar' ? 'English' : 'العربية'}
            </button>
        </div>
    );
}
