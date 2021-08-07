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
// //���ض���
// function scrollToTop() {
//     $('#back_top').click(function () {
//         changeBackTopText();
//         //�ܾ���
//         let distance = $('html').scrollTop() + $('body').scrollTop();
//         //heightΪ�˸��µ�ǰ�������ĸ߶ȶ���
//         let height = $('html,body');
//         //��ʱ��(500ms)
//         let time = 500;
//         //ÿ���intervalTimeʱ�����һ��
//         let intervalTime = 50;
//         //����ÿ�λ����ľ���
//         let itemDistance = distance / (time / intervalTime);
//         //ʹ��ѭ����ʱ�����Ϲ���
//
//         let intervalId = setInterval(function () {
//             distance -= itemDistance;
//             if (distance <= 0) {//���ﶥ����ֹͣ��ʱ��
//                 distance = 0;
//                 clearInterval(intervalId);
//             }
//             //���µ�ǰ�������ĸ߶�
//             height.scrollTop(distance);
//         }, intervalTime);
//
//         let aTimeOut = setTimeout(function () {
//             returnBackTopText();
//             clearTimeout(aTimeOut);
//         }, 3000)
//     });
// }
// //���ض�����ť�������¼�
// function btnMouseInOut() {
//     $('#back_top').hover(changeBackTopText(),returnBackTopText())
// }
// //�ı䷵�ض�����ť����
// function changeBackTopText() {
//     let $btn = $('#back_top');
//     $("#top-ico").addClass("hidden");
//     $btn.find("#top-msg").text("����");
//     $btn.find("#top-msg2").text("����");
//     console.log($("#top-msg").text())
// }
// //��ԭ����
// function returnBackTopText() {
//     let $btn = $('#back_top');
//     $("#top-ico").removeClass("hidden");
//     $btn.find("#top-msg").empty();
//     $btn.find("#top-msg2").empty();
// }