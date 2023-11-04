from django import forms
from django.db import models
from django.http import HttpResponseRedirect
from django.utils import timezone

from modelcluster.fields import ParentalKey, ParentalManyToManyField
from wagtail.contrib.routable_page.models import RoutablePageMixin, path
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
        context = super().get_context(request)
        
        # filter(date__lte=timezone.now())で絞りたいけどPageobjにはdate引数が無いので条件分岐
        pollspage_query = self.get_children().specific()
        for query in pollspage_query:
            if timezone.now().date() < query.date or not query.questions.all():
                query.live = False
                query.save()
            else:
                query.live = True
                query.save()
            
        pollspages = pollspage_query.live().order_by('-id')[:5]
        context['pollspages'] = pollspages
        return context


# Wagtailモデル
class PollsPage(RoutablePageMixin, Page):
    date = models.DateField("Post date")
    authors = ParentalManyToManyField('polls.Author', blank=True)
    parent_page_types = ['polls.PollsIndexPage']

    content_panels = Page.content_panels + [
            # 日付と作成者をグループ化して読みやすくする
            MultiFieldPanel([
                # 作成者フィールドをチェックボックスのウィジェットにする
                FieldPanel('authors', widget=forms.CheckboxSelectMultiple),
            ], heading="Polls information"),
            FieldPanel('date'),
            InlinePanel('questions', label="Questions"),
    ]

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
        verbose_name = "投票する"

    
class PollsPageChoice(Orderable):
    """PollsPageモデルの子モデル"""

    # related_nameはモデル名の代わりに使用する名前（関連モデル.questions.choice_textのような）。
    question = ParentalKey(PollsPage, on_delete=models.CASCADE, related_name='questions')
    # question = models.ForeignKey(PollsPage, on_delete=models.CASCADE, related_name='questions')
    choice_text = models.CharField(blank=True, max_length=250)
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

