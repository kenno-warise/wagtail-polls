from django import forms
from django.db import models
from django.http import HttpResponseRedirect
from django.utils import timezone

from modelcluster.fields import ParentalKey, ParentalManyToManyField
from wagtail.contrib.routable_page.models import RoutablePageMixin, path
from wagtail.admin.forms import WagtailAdminPageForm
from wagtail.models import Page, Orderable
from wagtail.fields import RichTextField
from wagtail.admin.panels import FieldPanel, InlinePanel, MultiFieldPanel
from wagtail.snippets.models import register_snippet


# Wagtailモデル
class PollsIndexPage(Page):
    intro = RichTextField(blank=True)
    # 親ページタイプの制御
    parent_page_types = ['wagtailcore.Page']
    # 子ページタイプの制御
    subpage_types = ['polls.PollsPage']

    content_panels = Page.content_panels + [
            FieldPanel('intro'),
    ]

    def get_context(self, request):
        """本日から過去の要素とchoice_textの要素が存在するか絞り込む"""
        
        context = super().get_context(request)

        if request.user.is_authenticated:
            pollspages = self.get_children().live().order_by('-id')
        else:
            pollspages = self.get_children().live().filter(
                    pollspage__date__lte=timezone.now(),
                    pollspage__questions__choice_text__isnull=False
            ).distinct().order_by('-id')[:5]
        
        context['pollspages'] = pollspages
        return context


# PollsPage管理ページのカスタマイズ
class PollsPageForm(WagtailAdminPageForm):

    def clean(self):
        cleaned_data = super().clean()
        if 'date' in cleaned_data:
            date = cleaned_data['date']
            # 未来の日付且つ公開として保存しようとした場合にエラーを発生させる
            if date > timezone.now().date() and 'action-publish' in self.data:
                self.add_error('date', '未来の日付で保存する場合は非公開にする必要があります!!')
        return cleaned_data


# Wagtailモデル
class PollsPage(RoutablePageMixin, Page):
    date = models.DateField("Post date", blank=False)
    authors = ParentalManyToManyField('polls.Author', blank=True)
    parent_page_types = ['polls.PollsIndexPage']
    content_panels = Page.content_panels + [
            # 日付と作成者をグループ化して読みやすくする
            MultiFieldPanel([
                # 作成者フィールドをチェックボックスのウィジェットにする
                FieldPanel('authors', widget=forms.CheckboxSelectMultiple),
            ], heading="Polls information"),
            FieldPanel('date'),
            InlinePanel('questions', label="Questions", min_num=2),
    ]
    base_form_class = PollsPageForm

    @path('vote/')
    def vote(self, request):
        """質問を選択して送信した後の処理のテスト"""
        try:
            selected_choice = self.questions.get(id=request.POST['choice'])
        except KeyError:
            context = super().get_context(request)
            context['error_message'] = "You didn't select a choice."
            return self.render(
                    request,
                    'polls/polls_page.html',
                    context_overrides=context,
            )
            
        # voteフィールドに整数１を加算して保存
        selected_choice.vote += 1
        selected_choice.save()
        # 「/polls/slug/result/」を生成して変数に格納
        url = self.url + self.reverse_subpage('result')
        return HttpResponseRedirect(url)
    
    @path('result/')
    def result(self, request):
        return self.render(
                request,
                template='polls/polls_result_page.html',
        )
    
    class Meta:
        # 作成するページのタイプを選択する際の表示名を定義
        verbose_name = "質問の追加"
    

class PollsPageChoice(Orderable):
    """PollsPageモデルの子モデル"""

    # related_nameはモデル名の代わりに使用する名前（関連モデル.questions.choice_textのような）。
    question = ParentalKey(PollsPage, on_delete=models.CASCADE, related_name='questions')
    # question = models.ForeignKey(PollsPage, on_delete=models.CASCADE, related_name='questions')
    choice_text = models.CharField(blank=False, max_length=250)
    vote = models.IntegerField(default=0)

    panels = [
            FieldPanel('choice_text'),
            FieldPanel('vote'),
      ]


# Wagtailデコレーター
@register_snippet
class Author(models.Model):
    name = models.CharField(max_length=255)
    author_image = models.ForeignKey(
            'wagtailimages.Image', null=True, blank=True,
            on_delete=models.SET_NULL, related_name='+'
    )

    # スニペットではスラッグや公開日などのフィールドが要らない為context_panelsではなくpanelsにしている
    panels = [
            FieldPanel('name'),
            FieldPanel('author_image'),
    ]

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = 'Authors'

