import { Button } from "@/components/ui/button";

type ErrorCardProps = {
  title?: string;
  message: string;
  onRetry?: () => void;
};

export default function ErrorCard({
  title = "Something went wrong",
  message,
  onRetry,
}: ErrorCardProps) {
  return (
    <div className="rounded-lg border border-red-300 bg-red-50 p-6">

      <h3 className="font-semibold text-red-700">
        {title}
      </h3>

      <p className="mt-2 text-sm text-red-600">
        {message}
      </p>

      {onRetry && (
        <Button
          variant="outline"
          className="mt-4"
          onClick={onRetry}
        >
          Retry
        </Button>
      )}

    </div>
  );
}