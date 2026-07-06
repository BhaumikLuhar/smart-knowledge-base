type LoadingStateProps = {
  title?: string;
  description?: string;
};

export default function LoadingState({
  title = "Loading...",
  description = "Please wait while we load the data.",
}: LoadingStateProps) {
  return (
    <div className="flex flex-col items-center justify-center py-16 text-center">

      <div className="h-10 w-10 animate-spin rounded-full border-4 border-muted border-t-primary" />

      <h3 className="mt-6 text-lg font-semibold">
        {title}
      </h3>

      <p className="mt-2 text-sm text-muted-foreground">
        {description}
      </p>

    </div>
  );
}