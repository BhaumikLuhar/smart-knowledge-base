import { Card } from "@/components/ui/card";

interface StatCardProps {
  title: string;

  value: string | number;

  subtitle?: string;
}

export default function StatCard({
  title,
  value,
  subtitle,
}: StatCardProps) {
  return (
    <Card className="p-6">

      <div className="space-y-2">

        <p className="text-sm text-muted-foreground">
          {title}
        </p>

        <h2 className="text-3xl font-bold">
          {value}
        </h2>

        {subtitle && (
          <p className="text-xs text-muted-foreground">
            {subtitle}
          </p>
        )}

      </div>

    </Card>
  );
}