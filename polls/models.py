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


class Polls(Page):
    """pollsアプリのトップページ"""

    intro = RichTextField(blank=True)

    # 管理ページにフィールドのフォームを設定する
    content_panels = Page.content_panels + [
            FieldPanel('intro'),
    ]
    # 親ページタイプの制御
    parent_page_types = ['home.HomePage']
    # parent_page_types = ['wagtailcore.Page']
    # 子ページタイプの制御
    subpage_types = ['polls.Question']
    # 独自のテンプレートファイルの設定
    template = 'polls/index.html'

    def get_context(self, request):
        """本日から過去の要素とchoice_textの要素が存在するか絞り込む"""
        
        context = super().get_context(request)

        if request.user.is_authenticated:
            pollspages = self.get_children().live().order_by('-id')
        else:
            pollspages = self.get_children().live().filter(
                    question__pub_date__lte=timezone.now(),
                    question__choices__choice_text__isnull=False
            ).distinct().order_by('-id')[:5]
        
        context['pollspages'] = pollspages
        return context


class QuestionForm(WagtailAdminPageForm):
    """Questionモデルの管理ページカスタマイズ"""

    def clean(self):
        """フォームに入力されたデータの検査"""
        cleaned_data = super().clean()
        if 'pub_date' in cleaned_data:
            date = cleaned_data['pub_date']
            # 未来の日付且つ公開として保存しようとした場合にエラーを発生させる
            if date > timezone.now().date() and 'action-publish' in self.data:
                self.add_error('pub_date', '未来の日付で保存する場合は非公開にする必要があります!!')
        return cleaned_data


class Question(RoutablePageMixin, Page):
    pub_date = models.DateField("Post date", blank=False)
    authors = ParentalManyToManyField('polls.Author', blank=True)
    content_panels = Page.content_panels + [
            # 日付と作成者をグループ化して読みやすくする
            MultiFieldPanel([
                # 作成者フィールドをチェックボックスのウィジェットにする
                FieldPanel('authors', widget=forms.CheckboxSelectMultiple),
            ], heading="Polls information"),
            FieldPanel('pub_date'),
            InlinePanel('choices', label="Choices", min_num=2),
    ]
    parent_page_types = ['polls.Polls']
    template = 'polls/detail.html'
    # カスタムフォームの設定
    base_form_class = QuestionForm

    # URLパターンの追加
    @path('vote/')
    def vote(self, request):
        """質問を選択して送信した後の処理のテスト"""
        
        try:
            selected_choice = self.choices.get(id=request.POST['choice'])
        except KeyError: # choiceキーが取得できなければエラーを表示してやり直す
            context = super().get_context(request)
            context['error_message'] = "You didn't select a choice."
            return self.render(
                    request,
                    'polls/detail.html',
                    context_overrides=context,
            )
            
        # votesフィールドに整数１を加算して保存
        selected_choice.votes += 1
        selected_choice.save()
        # 「/polls/slug/results/」を生成して変数に格納
        url = self.url + self.reverse_subpage('results')
        return HttpResponseRedirect(url)
    
    @path('results/')
    def results(self, request):
        """投票結果が表示するページ"""

        return self.render(
                request,
                template='polls/results.html',
        )
    
    class Meta:
        # 作成するページのタイプを選択する際の表示名を定義
        verbose_name = "Choice text"
    

class Choice(Orderable):
    """Questionモデルの子モデル"""

    # related_nameはモデル名の代わりに使用する名前（関連モデル.choices.choice_textのような）。
    # question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='choices')
    question = ParentalKey(Question, on_delete=models.CASCADE, related_name='choices')
    choice_text = models.CharField(blank=False, max_length=250)
    votes = models.IntegerField(default=0)

    panels = [
            FieldPanel('choice_text'),
            FieldPanel('votes'),
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

