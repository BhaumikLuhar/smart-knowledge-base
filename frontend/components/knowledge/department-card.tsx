import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";

interface Props {
  name: string;
  count: number;
}

export default function DepartmentCard({
  name,
  count,
}: Props) {
  return (
    <Card>
      <CardContent className="p-5">
        <div className="flex justify-between items-center">
          <div>
            <h3 className="font-semibold text-lg">
              {name}
            </h3>

            <p className="text-sm text-muted-foreground">
              Department
            </p>
          </div>

          <Badge>
            {count} docs
          </Badge>
        </div>
      </CardContent>
    </Card>
  );
}