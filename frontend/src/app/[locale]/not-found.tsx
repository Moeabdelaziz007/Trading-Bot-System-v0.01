import { notFound } from 'next/navigation';
import { setRequestLocale } from 'next-intl/server';

export default function NotFound({ params }: { params: { locale: string } }) {
    // Enable static rendering for this page
    setRequestLocale(params.locale);
    
    return notFound();
}