import datetime

from django.conf import settings
from django.utils import timezone
from wagtail.test.utils import WagtailPageTestCase
from wagtail.test.utils.form_data import nested_form_data, inline_formset, rich_text
from wagtail.models import Page

from home.models import HomePage
from .models import Polls, Question, Author


class WagtailPagesTests(WagtailPageTestCase):

    @classmethod
    def setUpTestData(cls):
        print('DEBUG'+' =', settings.DEBUG)
        # 各種親子関係のインスタンスを作成
        cls.home = HomePage.objects.get(title="Home")
        cls.polls = Polls(title="Polls")
        cls.question = Question(title="test", pub_date=datetime.datetime.now())
        cls.question.choices.create(choice_text="Past choice 1.", votes=0)
        cls.question.choices.create(choice_text="Past choice 2.", votes=0)

        # 親モデルから子モデルを追加
        cls.home.add_child(instance=cls.polls)
        cls.polls.add_child(instance=cls.question)

        # 各子モデルのインスタンスを保存して公開
        # cls.polls.save()
        # cls.question.save()
        cls.polls.save_revision().publish()
        cls.question.save_revision().publish()
    
    def test_page_routing(self):
        """各インスタンスのページにルーティング（特定のURLにアクセス）した時、404が表示されない事をアサート"""

        self.assertPageIsRoutable(self.home, msg="HomePageのテスト")
        self.assertPageIsRoutable(self.polls, msg="Pollsのテスト")
        self.assertPageIsRoutable(self.question, msg="Questionのテスト")
        self.assertPageIsRoutable(self.question, route_path="vote/", msg="Questionのテスト")
        self.assertPageIsRoutable(self.question, route_path="results/", msg="Questionのテスト")

    def test_question_rendering(self):
        """エラーを発生させることなくページをレンダリング（表示・可視化）できることをアサートする"""

        self.assertPageIsRenderable(self.question)
        self.assertPageIsRenderable(self.question, route_path="vote/", post_data={"choice": 1}, accept_redirect=True)

    def test_editability(self):
        """致命的なエラーを発生させることなく、ページ編集ビューがページに対して機能することをアサートします。"""

        self.assertPageIsEditable(
                self.polls,
                post_data=nested_form_data({
                    'title': 'Polls',
                    'intro': rich_text('Question!!'),
                })
        )

    def test_general_previewability(self):
        """致命的なエラーを発生させることなく、
        ページのプレビュービューをページにロードできることをアサートします。
        このアサーションはモデルのpreview_modesをオーバーライドし、
        さまざまなプレビューモードを使用しているページに有効。"""

        self.assertPageIsPreviewable(self.home)
        self.assertPageIsPreviewable(self.polls)
        self.assertPageIsPreviewable(self.question)

    def test_can_create_under_page(self):
        """親ページの下に作成できる子ページのアサート。
        似ているアサーションでassertAllowedParentPageTypesがある。"""

        self.assertCanCreateAt(HomePage, Polls)
        self.assertCanCreateAt(Polls, Question)

    def test_can_not_create_under_page(self):
        """親ページの下に作成できない子ページのアサート"""

        self.assertCanNotCreateAt(HomePage, Question)
        self.assertCanNotCreateAt(Question, Polls)

    def test_can_create_content_page(self):
        """管理画面内において指定されたポストデータで、指定された子のページを親の下で作成できるかアサート"""

        self.login()

        self.assertCanCreate(
                parent=self.home,
                child_model=Polls,
                data=nested_form_data({
                    'title': 'Polls2',
                    'intro': rich_text('Question!!'),
                })
        )
        # AssertionError: Creating a page failed for an unknown reason
        # self.assertCanCreate(
        #         parent=self.polls,
        #         child_model=Question,
        #         data=nested_form_data({
        #             'title': 'テスト２',
        #             'pub_date': timezone.now().date(),
        #             'choices': inline_formset([
        #                 {'choice_text': '選択１'},
        #                 {'votes': 0},
        #                 {'choice_text': '選択２'},
        #                 {'votes': 0},
        #             ], min=2)
        #         })
        # )
    
    def test_content_page_parent_pages(self):
        """ある子ページを作成できるページタイプが特定の親ページのみであることをテストします。
        モデルであるページタイプのフィールドparent_page_types属性に親ページを設定している場合に有効なテスト。"""

        self.assertAllowedParentPageTypes(Polls, {HomePage})
        self.assertAllowedParentPageTypes(Question, {Polls})

    def test_content_page_subpages(self):
        """ある親ページの下に作成できるページタイプが特定の子ページのみであることをテストします。
        モデルであるページタイプのフィールドsubpage_types属性に子ページを設定している場合に有効なテスト。"""

        self.assertAllowedSubpageTypes(Polls, {Question})


class PollsTests(WagtailPageTestCase):

    @classmethod
    def setUpTestData(cls):
        # 各種親子関係のインスタンスを作成
        cls.home = HomePage.objects.get(title="Home")
        cls.polls = Polls(title="Polls")
        cls.question = Question(title="test", pub_date=datetime.datetime.now())
        cls.question.choices.create(choice_text="Past choice 1.", votes=0)
        cls.question.choices.create(choice_text="Past choice 2.", votes=0)

        # 親モデルから子モデルを追加
        cls.home.add_child(instance=cls.polls)
        cls.polls.add_child(instance=cls.question)

        # 各子モデルのインスタンスを保存して公開
        # cls.polls.save()
        # cls.question.save()
        cls.polls.save_revision().publish()
        cls.question.save_revision().publish()

    def test_polls_view(self):
        """目的のビューにインスタンスが出力されるか"""

        res = self.client.get("/polls/")
        query = Page.objects.type(Question).live().filter(
                question__pub_date__lte=timezone.now(),
                question__choices__choice_text__isnull=False
        ).distinct().order_by('-id')[:5]
        self.assertQuerysetEqual(res.context["pollspages"], query)

    def test_polls_view_authenticated(self):
        """認証されたユーザーで目的のビューを表示するか"""

        self.login()
        res = self.client.get("/polls/")
        query = Page.objects.type(Question).all().order_by('-id')
        self.assertQuerysetEqual(res.context["pollspages"], query)


class QuestionTests(WagtailPageTestCase):

    @classmethod
    def setUpTestData(cls):
        # 各種親子関係のインスタンスを作成
        cls.home = HomePage.objects.get(title="Home")
        cls.polls = Polls(title="Polls")
        cls.question = Question(title="test", pub_date=datetime.datetime.now())
        cls.question.choices.create(choice_text="Past choice 1.", votes=0)
        cls.question.choices.create(choice_text="Past choice 2.", votes=0)

        # 親モデルから子モデルを追加
        cls.home.add_child(instance=cls.polls)
        cls.polls.add_child(instance=cls.question)

        # 各子モデルのインスタンスを保存して公開
        cls.polls.save()
        cls.question.save()
        # cls.polls.save_revision().publish()
        # cls.question.save_revision().publish()

    def test_choice_exception(self):
        """質問事項を選択せずに投票したあとのアサート"""

        url = self.question.url + self.question.reverse_subpage('vote')
        res = self.client.post(url)
        self.assertQuerysetEqual(
                res.context['error_message'],
                "You didn't select a choice."
        )
    
    def test_choice_redirect(self):
        """質問事項を選択して投票したあとのアサート"""
        
        url = self.question.url + self.question.reverse_subpage('vote')
        redirect_url = self.question.url + 'results/'
        res = self.client.post(url, {'choice': 1})
        self.assertRedirects(res, redirect_url)


class AuthorTests(WagtailPageTestCase):

    def test_author_name(self):
        """Authorモデルのstrメソッドではname属性が返されるアサート"""

        author = Author(name='Wagtail')
        self.assertEqual(author.__str__(), "Wagtail")

