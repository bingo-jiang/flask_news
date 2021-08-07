$(function () {
    navAdjust();
    btnPrimaryAdjust();
    //scrollToTop();
    //btnMouseInOut();
    initScroll();
});

function initScroll() {
    $(window).scroll(function () {
        let toTop = $(window).scrollTop();
        let pageHeight = $(window).height();
        if (toTop > pageHeight) {
            $("#back_top").removeClass("hidden");
        } else {
            $("#back_top").addClass("hidden");
        }
    })
}

function navAdjust() {
    const $myNav = $("#my_nav");
    $myNav.click(function () {
        let navFlag = $myNav.attr('aria-expanded');
        if (navFlag === "true") {
            $myNav.css("background-color", " #2b669a");
        } else {
            $myNav.css("background-color", " #2b669a");
        }
    });
}

function btnPrimaryAdjust() {
    let $btnPrimary = $(".btn-primary");
    $btnPrimary.click(function (e) {
        $(e.target).css("background-color", " #286090");
        let timeCount = setTimeout(function () {
            $(e.target).css("background-color", " #337ab7");
            clearTimeout(timeCount)
        }, 100)
    })
}
// //返回顶部
// function scrollToTop() {
//     $('#back_top').click(function () {
//         changeBackTopText();
//         //总距离
//         let distance = $('html').scrollTop() + $('body').scrollTop();
//         //height为了更新当前滚动条的高度而用
//         let height = $('html,body');
//         //总时间(500ms)
//         let time = 500;
//         //每间隔intervalTime时间滚动一次
//         let intervalTime = 50;
//         //计算每次滑动的距离
//         let itemDistance = distance / (time / intervalTime);
//         //使用循环定时器不断滚动
//
//         let intervalId = setInterval(function () {
//             distance -= itemDistance;
//             if (distance <= 0) {//到达顶部，停止定时器
//                 distance = 0;
//                 clearInterval(intervalId);
//             }
//             //更新当前滚动条的高度
//             height.scrollTop(distance);
//         }, intervalTime);
//
//         let aTimeOut = setTimeout(function () {
//             returnBackTopText();
//             clearTimeout(aTimeOut);
//         }, 3000)
//     });
// }
// //返回顶部按钮鼠标进出事件
// function btnMouseInOut() {
//     $('#back_top').hover(changeBackTopText(),returnBackTopText())
// }
// //改变返回顶部按钮内容
// function changeBackTopText() {
//     let $btn = $('#back_top');
//     $("#top-ico").addClass("hidden");
//     $btn.find("#top-msg").text("返回");
//     $btn.find("#top-msg2").text("顶部");
//     console.log($("#top-msg").text())
// }
// //还原内容
// function returnBackTopText() {
//     let $btn = $('#back_top');
//     $("#top-ico").removeClass("hidden");
//     $btn.find("#top-msg").empty();
//     $btn.find("#top-msg2").empty();
// }