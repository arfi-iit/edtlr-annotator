"""The index view."""
from annotation.models.annotation import Annotation
from annotation.models.evaluationinterval import EvaluationInterval
from dataclasses import dataclass
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from django.utils import timezone
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
        return UserStatistics(
            grand_total, per_status,
            [current_interval] if current_interval is not None else [])

    @staticmethod
    def get_current_interval() -> EvaluationInterval | None:
        """Get the current interval.

        Returns
        -------
        interval: EvaluationInterval
            The current interval or None.
        """
        now = timezone.now()
        return EvaluationInterval.objects\
                                 .filter(start_date__lte=now, end_date__gt=now)\
                                 .first()

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
            return interval.contains(dt.date())

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
