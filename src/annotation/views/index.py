"""The index view."""
from annotation.models.annotation import Annotation
from dataclasses import dataclass
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from django.views import View
from itertools import groupby


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
    per_year: list[tuple[int, StatisticItem]]


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
        per_year = UserStatisticsCalculator.calculate_stats_per_year(
            annotations)
        return UserStatistics(grand_total, per_status, per_year)

    @staticmethod
    def calculate_stats_per_year(
            annotations: list[Annotation]) -> list[tuple[int, StatisticItem]]:
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

        def get_group_key(annotation):
            if annotation.row_update_timestamp is not None:
                return annotation.row_update_timestamp.year

            return annotation.row_creation_timestamp.year

        annotations = sorted(annotations, key=get_group_key)
        grouped = groupby(annotations, get_group_key)
        return [(year, UserStatisticsCalculator.calculate_stats(list(group)))
                for year, group in grouped]

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
