let currentCid = 1; // 当前分类 id
let cur_page = 1; // 当前页
let total_page = 1;  // 总页数
let house_data_querying = true;   // 是否正在向后台获取数据
$(function () {
    updateNewsData();
    changeClickBtn();
    scrollEvent();
});

//数据更新
function updateNewsData() {
    // TODO 更新新闻数据
    let params = {
        "page": cur_page,
        "cid": currentCid,
        'per_page': 5
    };
    const GET_NEWS_URL = "/get_news";
    $.ajax({
        url: GET_NEWS_URL,
        data: params,
        type: "GET",
        dataType: "JSON",
        success: function (res) {
            house_data_querying = false;
            if (res.status) {
                total_page = res.totalPage;
                // 如果当前页数为1，则清空原有数据
                if (cur_page === 1) {
                    $(".news-container").html('')
                }
                // 当前页数递增
                cur_page += 1;
                // 显示数据
                for (let i = 0; i < res.newsList.length; i++) {
                    let news = res.newsList[i];
                    let content = '<a href="/news/' + news.id + '"><div class="new-item">';
                    content += '<div class="clearfix row row-no-gutter new-img-and-title">';
                    content += '<div class="col-xs-4 col-md-2 col-lg-2">';
                    content += '<img class="img" src="' + news.index_image_url + '" alt="pic_0' + news.id + '">';
                    //content += '<img class="img" src="/static/images/default.jpg" alt="pic_0' + news.id + '">';
                    content += '</div><div class="col-xs-8 col-md-10 col-lg-10">';
                    content += '<h4 class="title">' + news.title + '</h4>';
                    content += '<p class="hidden-xs hidden-sm">' + news.digest + '</p>';
                    content += '</div></div><div class="mini-show-div row clearfix">';
                    content += '<p class="pull-right col-xs-12 col-md-12 col-lg-12">';
                    if (news.author.nick_name.length !== 0) {
                        content += '<span class="mini-show">' + news.author.nick_name + '</span>';
                    }
                    content += '<span class="mini-show left-5">@发布于' + news.create_time + '</span>';
                    content += '<span class="mini-show left-5">来源于:' + news.source + '</span>';
                    content += '</p></div>';
                    content += '</div></a>';
                    //console.log(content);
                    $(".news-container").append(content)
                }
            } else {
                let errorImg = '<div class="err-img-div"><img class="err-img" src="' + res.error + '" alt="None"></div>';
                $(".news-container").append(errorImg);
            }
        }
    });
}

//首页分类切换点击事件
function changeClickBtn() {
    $('#my_nav_bar1 li a').click(function () {
        let showWidth = $(window).width();
        let pageWidth = $(document).width();
        if (showWidth <= 768 && pageWidth <= 768) {
            const $btnNav = $("#my_nav");
            const $navCollapse = $("#bs-example-navbar-collapse-1");
            $btnNav.attr("aria-expanded", false);
            $btnNav.addClass("collapsed");
            $navCollapse.attr("aria-expanded", false);
            $navCollapse.removeClass("in");
        }
        let clickCid = $(this).attr('data-cid');
        $('#my_nav_bar1 li a').each(function () {
            $(this).removeClass('active')
        });
        $(this).addClass('active');
        if (clickCid !== currentCid) {
            // 记录当前分类id
            currentCid = clickCid;
            // 重置分页参数
            cur_page = 1;
            total_page = 1;
            updateNewsData()
        }
    });
}

//页面滚动加载相关
function scrollEvent() {
    $(window).scroll(function () {
        // 浏览器窗口高度
        let showHeight = $(window).height();
        // 整个网页的高度
        let pageHeight = $(document).height();
        // 页面可以滚动的距离
        let canScrollHeight = pageHeight - showHeight;
        // 页面滚动了多少,这个是随着页面滚动实时变化的
        let nowScroll = $(document).scrollTop();
        if ((canScrollHeight - nowScroll) < 100) {
            // TODO 判断页数，去更新新闻数据
            if (!house_data_querying) {
                // 将`是否正在向后端查询新闻数据`的标志设置为真
                house_data_querying = true;
                // 如果当前页面数还没到达总页数
                if (cur_page < total_page) {
                    // 向后端发送请求，查询下一页新闻数据
                    updateNewsData();
                } else {
                    house_data_querying = false;
                }
            }
        }
    })
}
