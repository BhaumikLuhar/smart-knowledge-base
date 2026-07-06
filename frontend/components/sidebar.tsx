"use client";

import Link from "next/link";
import {
  LayoutDashboard,
  Database,
  MessageSquare,
  Users,
  Settings,
  ScrollText,
} from "lucide-react";

import { useAuth } from "@/contexts/AuthContext";
import { useRouter, usePathname } from "next/navigation";

export default function Sidebar() {

  const pathname = usePathname();

  const { user, logout } = useAuth();

  const router = useRouter();

  const navItems = [

    ...(user?.role === "admin"
      ? [

        {
          label: "Dashboard",
          href: "/dashboard",
          icon: LayoutDashboard,
        },

        {
          label: "Knowledge Base",
          href: "/knowledge-base",
          icon: Database,
        },

        {
          label: "Users",
          href: "/users",
          icon: Users,
        },

        {
          label: "Audit Logs",
          href: "/audit-logs",
          icon: ScrollText,
        },

      ]
      : []),

    {

      label: "Chat",

      href: "/chat",

      icon: MessageSquare,

    },

    {

      label: "Settings",

      href: "/settings",

      icon: Settings,

    },

  ];

  async function handleLogout() {

    await logout();

    router.replace(
      "/login"
    );
  }
  return (
    <aside className="w-64 border-r bg-background flex flex-col">
      <div className="p-6 border-b">
        <h2 className="font-bold text-lg">
          Smart Knowledge Bank
        </h2>
      </div>

      <nav className="flex-1 p-4 space-y-2">
        {navItems.map((item) => {
          const Icon = item.icon;

          return (
            <Link
              key={item.href}
              href={item.href}
              className={`flex items-center gap-3 rounded-md px-3 py-2 transition ${pathname === item.href
                ? "bg-primary text-primary-foreground"
                : "hover:bg-muted"
                }`}
            >
              <Icon className="h-4 w-4" />
              <span>{item.label}</span>
            </Link>
          );
        })}
      </nav>

      <div className="border-t p-4 space-y-3">

        <div>
          <p className="font-medium">
            {user?.full_name}
          </p>

          <p className="text-sm text-muted-foreground">
            {user?.role}
          </p>
        </div>

        <button
          onClick={handleLogout}
          className="w-full border rounded-md py-2 text-sm"
        >
          Logout
        </button>

      </div>
    </aside>
  );
}