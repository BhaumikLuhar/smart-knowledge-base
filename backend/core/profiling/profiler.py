import time


class PerformanceProfiler:

    def __init__(self):
        self.reset()

    def reset(self):
        self.timings: dict[str, list[float]] = {}
        self.starts = {}

    def start(self, name: str):
        self.starts[name] = time.perf_counter()

    def stop(self, name: str):

        start = self.starts.pop(name, None)

        if start is None:
            return

        duration = (
            time.perf_counter() - start
        ) * 1000

        self.timings.setdefault(
            name,
            []
        ).append(duration)

    def report(self):

        print("\n")
        print("=" * 90)
        print("PERFORMANCE PROFILE")
        print("=" * 90)

        rows = []

        for stage, values in self.timings.items():

            total = sum(values)

            rows.append(
                (
                    stage,
                    len(values),
                    total,
                    total / len(values),
                    min(values),
                    max(values),
                )
            )

        rows.sort(
            key=lambda x: x[2],
            reverse=True,
        )

        print(
            f"{'Stage':40}"
            f"{'Calls':>8}"
            f"{'Total':>12}"
            f"{'Avg':>12}"
            f"{'Min':>12}"
            f"{'Max':>12}"
        )

        print("-" * 90)

        for (
            stage,
            count,
            total,
            avg,
            minimum,
            maximum,
        ) in rows:

            print(
                f"{stage:40}"
                f"{count:>8}"
                f"{total:>10.2f}ms"
                f"{avg:>10.2f}ms"
                f"{minimum:>10.2f}ms"
                f"{maximum:>10.2f}ms"
            )

        print("=" * 90)


profiler = PerformanceProfiler()
