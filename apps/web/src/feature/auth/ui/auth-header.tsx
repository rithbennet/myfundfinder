import Link from "next/link"

export function AuthHeader() {
    return (
        <div className="flex items-center justify-between w-full max-w-md mx-auto mb-8">
            <Link href="/" className="text-2xl font-bold text-foreground">
                MYFundFinder
            </Link>
            <div className="text-sm text-muted-foreground">Checa404</div>
        </div>
    )
}
