# problems/views.py
import csv
from collections import defaultdict

from django.db.models import Q
from django.http import HttpResponse
from django.views import generic, View
from .forms import ProblemForm
from django.shortcuts import redirect
from django.shortcuts import render
from .models import ThoughtProcess, Problem, Tag
from django.urls import reverse_lazy
from django.views.generic import UpdateView
from .forms import ThoughtProcessForm

def start_page(request):
    problem_count = Problem.objects.count()
    process_count = ThoughtProcess.objects.count()

    context = {
        'problem_count': problem_count,
        'process_count': process_count,
    }
    return render(request, 'start_page.html', context)

# problems/views.py
def add_problem(request):
    if request.method == 'POST':
        form = ProblemForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('start_page')
    else:
        form = ProblemForm()

    return render(request, 'add_problem.html', {'form': form})

class ProblemUpdateView(UpdateView):
    model = Problem
    form_class = ProblemForm
    template_name = 'add_problem.html'
    success_url = reverse_lazy('start_page')  # 更新後にリダイレクトするURL

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = self.get_form()  # フォームをコンテキストに追加
        return context

# problems/views.py
def add_thought_process(request):
    if request.method == 'POST':
        form = ThoughtProcessForm(request.POST)
        if form.is_valid():
            new_form = form.save()

            selected_problems = form.cleaned_data['problems']

            for problems in selected_problems:
                problems.thought_processes.add(new_form)

            related_processes = form.cleaned_data['related_processes']
            for related_process in related_processes:
                related_process.related_processes.add(new_form)


            return redirect('start_page')
        else: print(form.errors)
    else:
        form = ThoughtProcessForm()

    return render(request, 'add_thought_process.html', {'form': form})


class ThoughtProcessUpdateView(UpdateView):
    model = ThoughtProcess
    form_class = ThoughtProcessForm
    template_name = 'add_thought_process.html'
    success_url = reverse_lazy('start_page')

    def get_form(self, form_class=None):
        form = super().get_form(form_class)

        # 更新時に表示されるproblemsの初期値を設定
        if self.object:
            form.fields['problems'].initial = self.object.problems.all()

        return form

    def form_valid(self, form):
        # Save the updated ThoughtProcess instance
        updated_form = form.save()

        # Get the selected problems from the form
        selected_problems = form.cleaned_data['problems']

        print(selected_problems)

        # Clear the existing thought processes related to the problems
        updated_form.problems.clear()

        # Associate the updated thought process with the selected problems
        for problem in selected_problems:
            problem.thought_processes.add(updated_form)

        return super().form_valid(form)

# problems/views.py
def visualization_page(request):
    thought_processes = ThoughtProcess.objects.all()

    # 各思考プロセスと紐づけられている問題数を取得
    data = {
        "nodes": [],
        "links": []
    }

    # ノードを作成
    for process in thought_processes:
        data["nodes"].append({
            "id": process.id,
            "name": process.process,
            "problem_count": process.problems.count()  # 紐付けられている問題の数
        })


    # 各思考プロセスの関連度を計算するための辞書
    related_scores = defaultdict(int)

    # すべての思考プロセスを取得
    thought_processes = ThoughtProcess.objects.prefetch_related('problems')

    # 思考プロセス同士の関連度を計算
    for tp1 in thought_processes:
        for tp2 in thought_processes:
            if tp1.id < tp2.id:  # 自分自身は除外
                shared_problems = tp1.problems.filter(id__in=tp2.problems.values_list('id', flat=True))
                related_scores[f"{tp1.id}, {tp2.id}"] += shared_problems.count()
                if shared_problems.count() >= 1:
                    data["links"].append({
                        "source": tp1.id,
                        "target": tp2.id
                    })


    # リンクを作成（思考プロセス同士の紐付け）
    """
    for process in thought_processes:
        for related_process in process.related_processes.all():
            data["links"].append({
                "source": process.id,
                "target": related_process.id
            })
    """

    # データをJSONに変換してテンプレートに渡す
    return render(request, 'visualization_page.html', {"data": data,"related_scores": related_scores})

class ProblemListView(generic.ListView):
    model = Problem
    template_name = 'problem_list.html'
    context_object_name = 'object_list'

    def get_queryset(self):
        queryset = Problem.objects.all()

        # GETパラメータを取得
        source_years = self.request.GET.getlist('source_year')
        source_universities = self.request.GET.getlist('source_university')
        source_faculties = self.request.GET.getlist('source_faculty')
        tags = self.request.GET.getlist('tags')
        thought_processes = self.request.GET.getlist('thought_processes')
        keyword = self.request.GET.get('keyword', '')

        # 出題年度でフィルタ
        if source_years:
            queryset = queryset.filter(source_year__in=source_years)

        # 出題大学でフィルタ
        if source_universities:
            queryset = queryset.filter(source_university__in=source_universities)

        # 出題学部でフィルタ
        if source_faculties:
            queryset = queryset.filter(source_faculty__in=source_faculties)

        # タグでフィルタ（複数選択可能）
        if tags:
            queryset = queryset.filter(tags__id__in=tags).distinct()

        # 思考プロセスでフィルタ（複数選択可能）
        if thought_processes:
            queryset = queryset.filter(thought_processes__id__in=thought_processes).distinct()

        # キーワード検索
        if keyword:
            queryset = queryset.filter(
                Q(source_university__icontains=keyword) |
                Q(source_faculty__icontains=keyword) |
                Q(good_points__icontains=keyword) |
                Q(usage_location__icontains=keyword)
            ).distinct()

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['tags'] = Tag.objects.all()
        context['thought_processes'] = ThoughtProcess.objects.all()
        context['source_years'] = Problem.objects.values_list('source_year', flat=True).distinct()
        context['source_universities'] = Problem.objects.values_list('source_university', flat=True).distinct()
        context['source_faculties'] = Problem.objects.values_list('source_faculty', flat=True).distinct()
        return context

class ProblemDetailView(generic.DetailView):
    model = Problem
    template_name = 'problem_detail.html'

class ProblemDeleteView(generic.DeleteView):
    model = Problem
    template_name = 'problem_confirm_delete.html'
    success_url = reverse_lazy('problem_list')

class ThoughtProcessListView(generic.ListView):
    model = ThoughtProcess
    template_name = 'thoughtprocess_list.html'
    context_object_name = 'object_list'

class ThoughtProcessDetailView(generic.DetailView):
    model = ThoughtProcess
    template_name = 'thoughtprocess_detail.html'

class ThoughtProcessDeleteView(generic.DeleteView):
    model = ThoughtProcess
    template_name = 'thoughtprocess_confirm_delete.html'
    success_url = reverse_lazy('thoughtprocess_list')


class ExportProblemCSV(View):
    def get(self, request, *args, **kwargs):
        # レスポンスをCSVファイルとして設定
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="problems.csv"'

        # CSVライターを作成
        writer = csv.writer(response)

        # ヘッダーを追加
        writer.writerow([
            'ID', '出題年度', '出題大学', '出題学部', 'BoxURL', '難易度', 'タグ', '思考プロセス', '良い点', '扱う場所'
        ])

        # データを追加
        problems = Problem.objects.all()
        for problem in problems:
            tags = ", ".join([tag.name for tag in problem.tags.all()])
            thought_processes = ", ".join([tp.process for tp in problem.thought_processes.all()])
            writer.writerow([
                problem.id, problem.source_year, problem.source_university, problem.source_faculty,
                problem.boxURL, problem.difficulty, tags, thought_processes,
                problem.good_points, problem.usage_location
            ])

        return response