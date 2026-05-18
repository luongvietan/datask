import NextAuth, { type NextAuthConfig } from "next-auth";
import GitHub from "next-auth/providers/github";
import Google from "next-auth/providers/google";

const DATASK_API_URL = process.env.DATASK_API_URL ?? "http://localhost:8000";

// Only register providers that have credentials configured
const providers: NextAuthConfig["providers"] = [];

if (process.env.GOOGLE_CLIENT_ID && process.env.GOOGLE_CLIENT_SECRET) {
  providers.push(
    Google({
      clientId: process.env.GOOGLE_CLIENT_ID,
      clientSecret: process.env.GOOGLE_CLIENT_SECRET,
    })
  );
}

if (process.env.GITHUB_ID && process.env.GITHUB_SECRET) {
  providers.push(
    GitHub({
      clientId: process.env.GITHUB_ID,
      clientSecret: process.env.GITHUB_SECRET,
    })
  );
}

export const { handlers, auth, signIn, signOut } = NextAuth({
  providers,

  callbacks: {
    async signIn({ user, account }) {
      if (!account || !user.email) return false;

      try {
        const res = await fetch(`${DATASK_API_URL}/v1/auth/oauth/upsert`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            provider: account.provider,
            provider_account_id: account.providerAccountId,
            email: user.email,
            name: user.name ?? null,
          }),
        });

        if (!res.ok) {
          console.error("OAuth upsert failed:", await res.text());
          return false;
        }

        const data = await res.json();
        (user as any).accountId = data.account_id;
        (user as any).tier = data.tier;
      } catch (err) {
        console.error("OAuth upsert error:", err);
        return false;
      }

      return true;
    },

    async jwt({ token, user }) {
      if (user) {
        token.accountId = (user as any).accountId;
        token.tier = (user as any).tier ?? "free";
      }
      return token;
    },

    async session({ session, token }) {
      if (token.accountId) {
        session.user.accountId = token.accountId as string;
        session.user.tier = (token.tier as string) ?? "free";
      }
      return session;
    },
  },

  pages: {
    signIn: "/login",
    error: "/login",
  },
});

// Extend NextAuth types
declare module "next-auth" {
  interface User {
    accountId?: string;
    tier?: string;
  }
  interface Session {
    user: {
      accountId?: string;
      tier?: string;
      name?: string | null;
      email?: string | null;
      image?: string | null;
    };
  }
}
