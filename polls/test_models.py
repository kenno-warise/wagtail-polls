import datetime

from wagtail.test.utils import WagtailPageTestCase
from wagtail.test.utils.form_data import nested_form_data, inline_formset, rich_text
from .models import PollsIndexPage, PollsPage, Author
from wagtail.models import Page


class WagtailPagesTests(WagtailPageTestCase):

    @classmethod
    def setUpTestData(cls):
        # PollsIndexPage.objects.create(title="Polls", path="000100010001", depth=3)
        # PollsPage.objects.create(title="test", path="0001000100010001", depth=4, date=datetime.datetime.now())

        # 各種親子関係のインスタンスを作成
        cls.page = Page.objects.get(title="Welcome to your new Wagtail site!")
        cls.pollsindex = PollsIndexPage(title="Polls")
        cls.pollspage = PollsPage(title="test", date=datetime.datetime.now())
        cls.pollspage.questions.create(choice_text="Past choice 1.", vote=0)

        # 親モデルから子モデルを追加
        cls.page.add_child(instance=cls.pollsindex)
        cls.pollsindex.add_child(instance=cls.pollspage)

        # 各子モデルのインスタンスを保存して公開
        cls.pollsindex.save_revision().publish()
        cls.pollspage.save_revision().publish()

    def test_page_routing(self):
        """各インスタンスのページにルーティング（特定のURLにアクセス）した時、404が表示されない事をアサート"""

        self.assertPageIsRoutable(self.page, msg="Pageのテスト")
        self.assertPageIsRoutable(self.pollsindex, msg="PollsIndexPageのテスト")
        self.assertPageIsRoutable(self.pollspage, msg="PollsPageのテスト")
        self.assertPageIsRoutable(self.pollspage, route_path="vote/", msg="PollsPageのテスト")
        self.assertPageIsRoutable(self.pollspage, route_path="result/", msg="PollsPageのテスト")

    def test_polls_rendering(self):
        """エラーを発生させることなくページをレンダリング（表示・可視化）できることをアサートする"""

        self.assertPageIsRenderable(self.pollspage)
        self.assertPageIsRenderable(self.pollspage, route_path="vote/", post_data={"choice": 1}, accept_redirect=True)

    def test_editability(self):
        """致命的なエラーを発生させることなく、ページ編集ビューがページに対して機能することをアサートします。"""

        self.assertPageIsEditable(
                self.pollsindex,
                post_data=nested_form_data({
                    'title': 'Polls2',
                    'intro': rich_text('Question!!'),
                })
        )

    def test_general_previewability(self):
        """致命的なエラーを発生させることなく、
        ページのプレビュービューをページにロードできることをアサートします。
        このアサーションはモデルのpreview_modesをオーバーライドし、
        さまざまなプレビューモードを使用しているページに有効。"""

        self.assertPageIsPreviewable(self.page)
        self.assertPageIsPreviewable(self.pollsindex)
        self.assertPageIsPreviewable(self.pollspage)

    def test_can_create_under_page(self):
        """親ページの下に作成できる子ページのアサート。
        似ているアサーションでassertAllowedParentPageTypesがある。"""

        self.assertCanCreateAt(Page, PollsIndexPage)
        self.assertCanCreateAt(PollsIndexPage, PollsPage)

    def test_can_not_create_under_page(self):
        """親ページの下に作成できない子ページのアサート"""

        self.assertCanNotCreateAt(Page, PollsPage)
        self.assertCanNotCreateAt(PollsPage, PollsIndexPage)

    def test_can_create_content_page(self):
        """管理画面内において指定されたポストデータで、指定された子のページを親の下で作成できるかアサート"""

        self.login()

        self.assertCanCreate(
                parent=self.page,
                child_model=PollsIndexPage,
                data=nested_form_data({
                    'title': 'Polls2',
                    'intro': rich_text('Question!!'),
                })
        )
        self.assertCanCreate(
                parent=self.pollsindex,
                child_model=PollsPage,
                data=nested_form_data({
                    'title': 'テスト２',
                    'date': datetime.date(2023, 10, 21),
                    'questions': inline_formset([])
                })
        )
    
    def test_content_page_parent_pages(self):
        """ある子ページを作成できるページタイプが特定の親ページのみであることをテストします。
        モデルであるページタイプのフィールドparent_page_types属性に親ページを設定している場合に有効なテスト。"""

        self.assertAllowedParentPageTypes(PollsIndexPage, {Page})
        self.assertAllowedParentPageTypes(PollsPage, {PollsIndexPage})

    def test_content_page_subpages(self):
        """ある親ページの下に作成できるページタイプが特定の子ページのみであることをテストします。
        モデルであるページタイプのフィールドsubpage_types属性に子ページを設定している場合に有効なテスト。"""

        self.assertAllowedSubpageTypes(PollsIndexPage, {PollsPage})


class PollsIndexPageTests(WagtailPageTestCase):

    @classmethod
    def setUpTestData(cls):
        # 各種親子関係のインスタンスを作成
        cls.page = Page.objects.get(title="Welcome to your new Wagtail site!")
        cls.pollsindex = PollsIndexPage(title="Polls")
        cls.pollspage = PollsPage(title="test", date=datetime.datetime.now())
        cls.pollspage.questions.create(choice_text="Past choice 1.", vote=0)

        # 親モデルから子モデルを追加
        cls.page.add_child(instance=cls.pollsindex)
        cls.pollsindex.add_child(instance=cls.pollspage)

        # 各子モデルのインスタンスを保存して公開
        cls.pollsindex.save_revision().publish()
        cls.pollspage.save_revision().publish()

    def test_pollsindexpage_view(self):
        """目的のビューにインスタンスが出力されるか"""

        res = self.client.get("/polls/")
        query = Page.objects.type(PollsPage).live().order_by('-first_published_at')
        self.assertQuerysetEqual(res.context["pollspages"], query)


class PollsPageTests(WagtailPageTestCase):

    @classmethod
    def setUpTestData(cls):
        # 各種親子関係のインスタンスを作成
        cls.page = Page.objects.get(title="Welcome to your new Wagtail site!")
        cls.pollsindex = PollsIndexPage(title="Polls")
        cls.pollspage = PollsPage(title="test", date=datetime.datetime.now())
        cls.pollspage.questions.create(choice_text="Past choice 1.", vote=0)

        # 親モデルから子モデルを追加
        cls.page.add_child(instance=cls.pollsindex)
        cls.pollsindex.add_child(instance=cls.pollspage)

        # 各子モデルのインスタンスを保存して公開
        cls.pollsindex.save_revision().publish()
        cls.pollspage.save_revision().publish()

    def test_choice_exception(self):
        """質問事項を選択せずに投票したあとのアサート"""

        url = self.pollspage.url + 'vote/'
        res = self.client.post(url)
        self.assertQuerysetEqual(res.context['error_message'], "You didn't select a choice.")
    
    def test_choice_redirect(self):
        """質問事項を選択して投票したあとのアサート"""
        
        url = self.pollspage.url + 'vote/'
        redirect_url = self.pollspage.url + 'result/'
        res = self.client.post(url, {'choice': 1})
        self.assertRedirects(res, redirect_url)


class AuthorTests(WagtailPageTestCase):

    def test_author_name(self):
        """Authorモデルのstrメソッドではname属性が返されるアサート"""

        author = Author(name='Wagtail')
        self.assertEqual(author.__str__(), "Wagtail")

