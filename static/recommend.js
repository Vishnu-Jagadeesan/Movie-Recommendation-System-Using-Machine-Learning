$(function() {
  $('#movie_list').css('display','none');
  $('#autoComplete').blur(function() {
    $('#movie_list').css('display','none');
  });
  
  const source = document.getElementById('autoComplete');
  const inputHandler = function(e) {
    $('#movie_list').css('display','block');
    if(e.target.value==""){
      $('.movie-button').attr('disabled', true);
    }
    else{
      $('.movie-button').attr('disabled', false);
    }
  }
  source.addEventListener('input', inputHandler);

  $('.fa-arrow-up').click(function(){
    $('html, body').animate({scrollTop:0}, 'slow');
  });

  $('.app-title').click(function(){
    window.location.href = '/';
  })

  $('.movie-button').on('click',function(){
    var title = $('.movie').val();
    $('#movie_list').css('display','none');
    if (title=="") {
      $('.results').css('display','none');
      $('.fail').css('display','block');
    }

    if (($('.fail').text() && ($('.footer').css('position') == 'absolute'))) {
      $('.footer').css('position', 'fixed');
    }
    else{
      load_details(title,true);
    }
  });
});

function recommendcard(id){
  $("#loader").fadeIn();
  load_details(id,false);
}

function load_details(search,isQuerySearch){
  let url = isQuerySearch ? 
    `/api/search?query=${encodeURIComponent(search)}` : 
    `/api/movie/${search}`;

  $.ajax({
    type: 'GET',
    url: url,
    success: function(movie){
      if(!isQuerySearch) {
        handleSingleMovie(movie);
      }
      else if(movie.results.length<1){
        showError();
      }
      else if(movie.results.length==1) {
        handleSingleResult(movie);
      }
      else{
        handleMultipleResults(movie);
      }
    },
    error: function(error){
      alert('Invalid Request - '+error);
      $("#loader").delay(500).fadeOut();
    },
  });
}

function handleSingleMovie(movie) {
  $("#loader").fadeIn();
  $('.fail').css('display','none');
  $('.results').delay(1000).css('display','block');
  get_movie_details(movie.id, movie.title, movie.original_title);
}

function handleSingleResult(movie) {
  $("#loader").fadeIn();
  $('.fail').css('display','none');
  $('.results').delay(1000).css('display','block');
  const result = movie.results[0];
  get_movie_details(result.id, result.title, result.original_title);
}

function handleMultipleResults(movie) {
  $("#loader").fadeIn();
  $('.fail').css('display','none');
  $('.results').delay(1000).css('display','block');

  $.ajax({
    type:'POST',
    data:JSON.stringify({movies_list: movie.results}),
    beforeSend: function() {
      $("#loader").fadeIn();
    },
    url:"/populate-matches",
    dataType: 'html',
    complete: function(){
      $("#loader").delay(1000).fadeOut();
    },
    success: function(response) {
      updateUI(response);
    }
  });
}

function get_movie_details(movie_id, movie_title, movie_title_org) {
  $.ajax({
    type:'GET',
    url:`/api/movie/${movie_id}`,
    success: function(movie_details){
      show_details(movie_details, movie_title, movie_title_org);
    },
    error: function(error){
      alert("API Error! - "+error);
      $("#loader").delay(500).fadeOut();
    },
  });
}

function show_details(movie_details, movie_title, movie_title_org){
  const imdb_id = movie_details.imdb_id;
  const poster = movie_details.poster_path ? 
    `https://image.tmdb.org/t/p/original${movie_details.poster_path}` : 
    '/static/movie_placeholder.jpeg';
  
  const recommendations = get_recommendations(movie_details.id);
  const movie_cast = get_movie_cast(movie_details.id);
  const ind_cast = get_individual_cast(movie_cast.cast_ids);

  const details = {
    title: movie_title,
    cast_ids: JSON.stringify(movie_cast.cast_ids),
    cast_names: JSON.stringify(movie_cast.cast_names),
    cast_chars: JSON.stringify(movie_cast.cast_chars),
    cast_profiles: JSON.stringify(movie_cast.cast_profiles),
    cast_bdays: JSON.stringify(ind_cast.cast_bdays),
    cast_bios: JSON.stringify(ind_cast.cast_bios),
    cast_places: JSON.stringify(ind_cast.cast_places),
    imdb_id: imdb_id,
    poster: poster,
    genres: movie_details.genres.map(g => g.name).join(', '),
    overview: movie_details.overview,
    rating: movie_details.vote_average,
    vote_count: movie_details.vote_count.toLocaleString(),
    rel_date: movie_details.release_date,
    release_date: new Date(movie_details.release_date).toDateString().split(' ').slice(1).join(' '),
    runtime: formatRuntime(movie_details.runtime),
    status: movie_details.status,
    rec_movies: JSON.stringify(recommendations.rec_movies),
    rec_posters: JSON.stringify(recommendations.rec_posters),
    rec_movies_org: JSON.stringify(recommendations.rec_movies_org),
    rec_year: JSON.stringify(recommendations.rec_year),
    rec_vote: JSON.stringify(recommendations.rec_vote),
    rec_ids: JSON.stringify(recommendations.rec_ids)
  };

  submitDetails(details);
}

function formatRuntime(minutes) {
  const hours = Math.floor(minutes/60);
  const mins = minutes%60;
  return hours ? `${hours} hour(s) ${mins} min(s)` : `${mins} min(s)`;
}

function get_individual_cast(cast_ids) {
  const cast_bdays = [];
  const cast_bios = [];
  const cast_places = [];
  
  cast_ids.forEach(cast_id => {
    $.ajax({
      type: 'GET',
      url: `/api/person/${cast_id}`,
      async: false,
      success: function(cast_details) {
        cast_bdays.push(new Date(cast_details.birthday).toDateString().split(' ').slice(1).join(' '));
        cast_bios.push(cast_details.biography || "Not Available");
        cast_places.push(cast_details.place_of_birth || "Not Available");
      }
    });
  });
  
  return { cast_bdays, cast_bios, cast_places };
}

function get_movie_cast(movie_id) {
  let cast = { cast_ids: [], cast_names: [], cast_chars: [], cast_profiles: [] };
  
  $.ajax({
    type: 'GET',
    url: `/api/movie/${movie_id}/credits`,
    async: false,
    success: function(credits) {
      const top_cast = credits.cast.slice(0, 10);
      top_cast.forEach(actor => {
        cast.cast_ids.push(actor.id);
        cast.cast_names.push(actor.name);
        cast.cast_chars.push(actor.character);
        cast.cast_profiles.push(actor.profile_path ? 
          `https://image.tmdb.org/t/p/original${actor.profile_path}` : 
          '/static/default.jpg');
      });
    }
  });
  
  return cast;
}

function get_recommendations(movie_id) {
  const result = { rec_movies: [], rec_posters: [], rec_movies_org: [], rec_year: [], rec_vote: [], rec_ids: [] };
  
  $.ajax({
    type: 'GET',
    url: `/api/movie/${movie_id}/recommendations`,
    async: false,
    success: function(response) {
      response.results.forEach(movie => {
        result.rec_movies.push(movie.title);
        result.rec_movies_org.push(movie.original_title);
        result.rec_year.push(new Date(movie.release_date).getFullYear());
        result.rec_vote.push(movie.vote_average);
        result.rec_ids.push(movie.id);
        result.rec_posters.push(movie.poster_path ? 
          `https://image.tmdb.org/t/p/original${movie.poster_path}` : 
          '/static/default.jpg');
      });
    }
  });
  
  return result;
}

function submitDetails(details) {
  $.ajax({
    type: 'POST',
    data: details,
    url: "/recommend",
    dataType: 'html',
    complete: function() {
      $("#loader").delay(500).fadeOut();
    },
    success: function(response) {
      $('.results').html(response);
      $('#autoComplete').val('');
      $('.footer').css('position','absolute');
      if ($('.movie-content')) {
        $('.movie-content').after('<div class="gototop"><i title="Go to Top" class="fa fa-arrow-up"></i></div>');
      }
      $(window).scrollTop(0);
    }
  });
}

function updateUI(response) {
  $('.results').delay(2000).html(response);
  $('#autoComplete').val('');
  $('.footer').css('position','relative');
  $('.social').css({'padding-bottom': '15px', 'margin-bottom': '0px'});
  $(window).scrollTop(0);
}

function showError() {
  $('.fail').css('display','block');
  $('.results').css('display','none');
  $("#loader").delay(500).fadeOut();
}

// Cold start loader – show on page load, hide when fully loaded
$(document).ready(function(){
  $('#coldstart-loader').fadeIn();
});

$(window).on('load', function(){
  $('#coldstart-loader').fadeOut(500);
});
