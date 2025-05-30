"""The index view."""
from annotation.models.annotation import Annotation
from dataclasses import dataclass
from datetime import datetime
from datetime import timezone
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from django.views import View


class IndexView(LoginRequiredMixin, View):
    """Implements the index view."""

    template_name = "annotation/index.html"

    def get(self, request):
        """Handle the GET request.

        Parameters
        ----------
        request: HttpRequest, required
            The request object.
        """
        annotations = Annotation.objects\
            .filter(user=request.user)\
            .order_by('-row_update_timestamp')
        statistics = UserStatisticsCalculator.calculate_statistics(annotations)
        annotations = [(a.id, a.title_word,
                        Annotation.AnnotationStatus(a.status).label,
                        a.status != Annotation.AnnotationStatus.COMPLETE)
                       for a in annotations]

        return render(request,
                      self.template_name,
                      context={
                          'annotations': annotations,
                          'statistics': statistics
                      })


@dataclass
class StatisticItem:
    """Defines a container for statistics."""

    num_annotations: int
    num_symbols: int


@dataclass
class TimeInterval:
    """Defines a time interval for which to compute statistics."""

    name: str
    start_date: datetime | None
    end_date: datetime | None

    def get_start_date(self, tz=None):
        """Get the start date if it's not None or datetime.min value.

        Returns
        -------
        start_date: datetime
            The value of start_date or datetime.min if the start_date is None.
        """
        if tz is None:
            return self.start_date if self.start_date is not None else datetime.min
        if self.start_date is None or self.start_date == datetime.min:
            return datetime.min.astimezone(tz)
        return self.start_date.astimezone(tz)

    def get_end_date(self, tz=None):
        """Get the end date if it isn't None or datetime.max value.

        Returns
        end_date: datetime
            The value of end_date or datetime.max if the end_date is None.
        """
        if tz is None:
            return self.end_date if self.end_date is not None else datetime.max
        if self.end_date is None or self.end_date == datetime.max:
            return datetime.max.astimezone(tz)
        return self.end_date.astimezone(tz)

    def contains(self, time_point: datetime) -> bool:
        """Check if the current interval contains the given point in time.

        Returns
        -------
        contains: bool
            True if the time point is greater or equal to start date, and less than end date; False otherwise.
        """
        date_time = time_point.astimezone(timezone.utc)
        return self.get_start_date(
            timezone.utc) <= date_time < self.get_end_date(timezone.utc)


INTERVALS = [
    TimeInterval("Semestrul II 2024-2025",
                 datetime(2025, 3, 6).astimezone(timezone.utc),
                 datetime(2025, 6, 30).astimezone(timezone.utc))
]


@dataclass
class UserStatistics:
    """Contains user statistics."""

    grand_total: StatisticItem
    per_status: list[tuple[Annotation.AnnotationStatus, StatisticItem]]
    current_interval: list[tuple[str, StatisticItem]]


class UserStatisticsCalculator:
    """Implements the logic for calculating user statistics."""

    @staticmethod
    def calculate_statistics(annotations: list[Annotation]) -> UserStatistics:
        """Calculate the statistics from the provided annotations.

        Parameters
        ----------
        annotations: list of Annotation, required
            The annotations for which to calculate statistics.

        Returns
        -------
        stats: UserStatistics
            The statistics.
        """
        grand_total = UserStatisticsCalculator.calculate_stats(annotations)
        per_status = UserStatisticsCalculator.calculate_stats_per_status(
            annotations)
        current_interval = UserStatisticsCalculator.calculate_stats_for_curent_interval(
            annotations)
        return UserStatistics(grand_total, per_status, [current_interval])

    @staticmethod
    def get_current_interval() -> TimeInterval | None:
        """Get the current interval.

        Returns
        -------
        interval: TimeInterval
            The current interval or None.
        """
        now = datetime.now(tz=None)
        for interval in INTERVALS:
            if interval.contains(now):
                return interval

        return None

    @staticmethod
    def calculate_stats_for_curent_interval(
            annotations: list[Annotation]) -> tuple[int, StatisticItem] | None:
        """Calculate the statistics per year.

        Parameters
        ----------
        annotations: list of Annotation, required
            The annotations of the user.

        Returns
        -------
        stats: list of (int, StatisticItem) tuples
            The statistics per year as a list of (year, StatisticItem) tuples.
        """
        interval = UserStatisticsCalculator.get_current_interval()
        if interval is None:
            return None
        annotations = [
            a for a in annotations
            if a.status != Annotation.AnnotationStatus.IN_PROGRESS
        ]

        def is_in_interval(interval, annotation):
            dt = annotation.row_creation_timestamp
            if annotation.row_update_timestamp is not None:
                dt = annotation.row_update_timestamp
            return interval.contains(dt)

        annotations = [a for a in annotations if is_in_interval(interval, a)]
        return (interval.name,
                UserStatisticsCalculator.calculate_stats(annotations))

    @staticmethod
    def calculate_stats_per_status(
        annotations: list[Annotation]
    ) -> list[tuple[Annotation.AnnotationStatus, StatisticItem]]:
        """Calculate the statistics per status.

        Parameters
        ----------
        annotations: list of Annotation, required
            The annotations of the user.

        Returns
        -------
        stats: list of (Annotation.AnnotationStatus, StatisticItem) tuples
            The statistics per year as a list of (status, StatisticItem) tuples.
        """
        statuses = [
            Annotation.AnnotationStatus.IN_PROGRESS,
            Annotation.AnnotationStatus.CONFLICT,
            Annotation.AnnotationStatus.COMPLETE
        ]
        stats = []

        for status in statuses:
            data = [a for a in annotations if a.status == status]
            item = UserStatisticsCalculator.calculate_stats(data)
            stats.append((status, item))
        return stats

    @staticmethod
    def calculate_stats(annotations: list[Annotation]) -> StatisticItem:
        """Calculate the statistics for the provided list of annotations.

        Parameters:
        ----------
        annotations: list of Annotation, required
            The annotations from which to calculate the statistics.

        Returns
        -------
        stats: StatisticItem
            The statistics calculated from the annotations.
        """
        num_symbols = sum([
            len(a.text) for a in annotations
            if a.status != Annotation.AnnotationStatus.IN_PROGRESS
        ])
        return StatisticItem(num_annotations=len(annotations),
                             num_symbols=num_symbols)
