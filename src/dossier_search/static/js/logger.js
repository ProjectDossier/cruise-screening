$(document).ready(function () {
  console.log("document loaded");

});
const aoi_dtl = {}; // details of AOIs
const interaction_events = []; // array of interaction events added chronologically

function get_ts_h(ms_from_epoch) {
  return moment(parseInt(ms_from_epoch))
      .format('YYYY-MM-DD HH:mm:ss.SSS');
}

function get_bb_details(jquery_elem) {
  // jquery element does not contain getBoundingClientRect()
  //so we need the underlying html element using [0]
  const e = jquery_elem[0];

  const bb_rect = e.getBoundingClientRect();

  // absolute bounding box (w.r.t. screen, for eye-tracker coordinates)
  // experimental: https://stackoverflow.com/a/29370069
  // will not work if dev toolbar or other window
  // decreases viewport width from the bottom
  const screen_x1 = window.screenX // window position relative to screen
      +
      bb_rect.left;

  const screen_y1 = window.screenY // window position relative to screen
      +
      window.outerHeight - window.innerHeight // height of navigation/toolbar
      +
      bb_rect.top;

  const screen_x2 = screen_x1 + bb_rect.width;
  const screen_y2 = screen_y1 + bb_rect.height;

  const page_x1 = bb_rect.left + window.scrollX;
  const page_y1 = bb_rect.top + window.scrollY;
  const page_x2 = page_x1 + bb_rect.width;
  const page_y2 = page_y1 + bb_rect.height;

  const res_obj = {
      //relative to webpage
      page_x1: parseInt(page_x1),
      page_y1: parseInt(page_y1),
      page_x2: parseInt(page_x2),
      page_y2: parseInt(page_y2),

      // relative to screen / monitor
      screen_x1: parseInt(screen_x1),
      screen_y1: parseInt(screen_y1),
      screen_x2: parseInt(screen_x2),
      screen_y2: parseInt(screen_y2),

      // bounding_rect: x, y, width, height, top, right, bottom, left
      bounding_rect: bb_rect,
  }
  return res_obj
}


$('[data-aoi]').on('mouseup', function (e) {
  e.stopPropagation(); // prevent parent AOIs from logging this event

  const _ts = new Date().getTime();
  const aoi = $(e.target).closest('[data-aoi]'); // gets the closest AOI for this click

  // add to log array
  interaction_events.push({
      ev_ts: _ts,
      ev_ts_h: get_ts_h(_ts),
      ev_name: 'M_CLICK',
      ev_dur: 0, // mouse "click" has no duration
      mouse_x: e.pageX,
      mouse_y: e.pageY,
      closest_aoi: aoi.data('aoi'),
      target: get_bb_details($(e.target)),
  });

  // update aggegrate count on closest aoi element
  if (aoi.data('tot_click_ct')) { // already been clicked
      aoi.data('tot_click_ct', aoi.data('tot_click_ct') + 1); // add one
  } else { // first click
      aoi.data('tot_click_ct', 1); // initialize the count
  }
});



const HOVER_THRESH = 10; // log hover events only >= 100ms

$('[data-aoi]').hover(
  //mouseover handler
  function (e) {
      e.stopPropagation(); // prevent parent AOIs from logging this event
      const aoi = $(e.target).closest('[data-aoi]');
      aoi.data('hover_st', new Date().getTime()); //record the hover start time
  },
  //mouseout handler
  function (e) {
      e.stopPropagation(); // prevent parent AOIs from logging this event

      const aoi = $(e.target).closest('[data-aoi]');
      const hover_end = new Date().getTime(); //grab the end time
      const hover_dur = (hover_end - aoi.data('hover_st')); //calculate the difference in ms

      // log result  on closest aoi element
      if (aoi.data('tot_hover_dur')) { // already hovered
          aoi.data('tot_hover_dur', aoi.data('tot_hover_dur') + hover_dur); // add current dur
      } else { // first hover
          aoi.data('tot_hover_dur', hover_dur); // initialize the count
      }

      if (hover_dur >= HOVER_THRESH) {
          // add to log array
          interaction_events.push({
              ev_ts: aoi.data('hover_st'),
              ev_ts_h: get_ts_h(aoi.data('hover_st')),
              ev_name: 'M_HOVER',
              ev_dur: hover_dur,
              mouse_x: e.pageX,
              mouse_y: e.pageY,
              closest_aoi: aoi.data('aoi'),
              target: get_bb_details($(e.target)),
          });
      }
      console.log(interaction_events);
  }
);


$("#submit").click(function () {
  console.log('submit was clicked');
  $('[data-aoi]').each(function (index) {
      const aoi_name = $(this).data('aoi');
      // object of objects, initialized at start
      aoi_dtl[aoi_name] = {
          aoi_name: aoi_name, // redundant
          tot_click_ct: $(this).data('tot_click_ct') || 0,
          tot_hover_dur: $(this).data('tot_hover_dur') || 0, // in milliseconds
          // get bounding box details of AOI
          ...get_bb_details($(this), true, true),
      };
  });
  console.log(aoi_dtl);
});



// append log data to existing form on the webpage
const form = $('form#api_form');

$('<input>', {
  type: 'hidden',
  name: `aoi_dtl`,
  value: JSON.stringify(aoi_dtl),
}).appendTo($(form));

$('<input>', {
  type: 'hidden',
  name: `interaction_events`,
  value: JSON.stringify(interaction_events),
}).appendTo($(form));