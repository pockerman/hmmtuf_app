$(function () {
  var state = 0;

  $("#add_state").on("click", function () {
    if (state < 6) {
      $("#state-group").append(
        `
        <fieldset class="mb-2 p-2">
        <legend>State ${state+1}</legend>
        <div class="state mb-2 mt-2">
        <div class="form-group mb-2">
        <label for="st_name">Name of state:</label>
        <input type="text" name="st_name[]" class="form-control">
        </div>
        <div class="row p-2">
        <button type="button" class="btn btn-light single-component col-4 form-control m-2">Single Component</button>
        <button type="button" class="btn btn-light mix-component form-control col-4 form-control m-2">Mixture Component</button>
        </div>
        <div class="component-div"></div>
        </div>
        </fieldset>
      `
        );
        if(state+1>1){
            $('.prob').show();

        }
        
      state++;

      if($('#IPV-group').is(':visible')){
          
        $('#add_IPV').click();
    }
    } else {
      alert("You can add only 6 states");
    }

    
  });
   

  // Single Component Structure
  $(document).on("click",".single-component" ,function(){

    var elem = $(this).parent().parent().find(".component-div");
    if (elem.is(":visible")) {
      elem.empty();
      elem.hide();
      $(this).parent().find('.mix-component').attr('disabled',false);

    }
    elem.append(`  
    <div class="componentItem">
    <div class="form-group">
        <div class="row p-2">
            <button type="button" class="btn btn-light normal-com col-4 form-control m-2">Normal</button>
            <button type="button" class="btn btn-light uniform-com form-control col-4 form-control m-2">Uniform</button>
        </div>

        <div class="single-com-view"></div>
    </div>  
    </div>
    `);
    console.log(elem);
    elem.show();
    $(this).attr('disabled',true);

  })
    // Mixture Componet Strucutre
  $(document).on("click",".mix-component", function () {

    var elem = $(this).parent().parent().find(".component-div");
    if (elem.is(":visible")) {
      elem.empty();
      elem.hide();
      $(this).parent().find('.single-component').attr('disabled',false);
    }
    elem.append(`

       <button type="button" class="btn btn-light add_M_com col-4 form-control m-2">Add Component</button>
       <div class="componentGroup"></div>
    `);
    elem.show();
    $(this).attr('disabled',true);
  });

  $(document).on('click', '.normal-com' , function(){

    var elem = $(this).parent().parent().find(".single-com-view");
    if (elem.is(":visible")) {
      elem.empty();
      elem.hide();
      $(this).parent().find('.uniform-com').attr('disabled',false);
    }
    elem.append(`
        <div class="row mb-2">
            <div class="col-6">
                <div class ="control-group">
                    <label for="single_com_m1">m1</label>
                    <input type="text" class="form-control" name="single_com_m1[]" >
                </div>
            </div>
            <div class="col-6">
                <div class ="control-group">
                    <label for="single_com_m2">m2</label>
                    <input type="text" class="form-control" name="single_com_m2[]" >
                </div>
            </div>
        </div>
        <div class="row">
            <div class="col-12">
                <div class="form-group">
                    <label for="single_com_sd">Stander Daviation:</label>
                    <input type="number" step="0.1" min="0.01" class="form-control mb-2" name="single_com_sd[]">
                </div>
            </div>
        </div>
    `)
    elem.show();
    $(this).attr('disabled',true);
  });

  $(document).on('click', '.uniform-com' , function(){

    var elem = $(this).parent().parent().find(".single-com-view");
    if (elem.is(":visible")) {
      elem.empty();
      elem.hide();
      $(this).parent().find('.normal-com').attr('disabled',false);
    }

    elem.append(`
        <div class="form-group">
        <div class="row">
            <div class="col-6">
                <div class ="control-group">
                    <label for="single_com_l1">l1</label>
                    <input type="text" class="form-control" name="single_com_l1[]" >
                </div>
            </div>
            <div class="col-6">
                <div class ="control-group">
                    <label for="single_com_l2">l2</label>
                    <input type="text" class="form-control" name="single_com_l2[]" >
                </div>
            </div>
        </div>
        <div class="row">
        <div class="col-6">
            <div class ="control-group">
                <label for="single_com_u1">u1</label>
                <input type="text" class="form-control" name="single_com_u1[]" >
            </div>
        </div>
        <div class="col-6">
            <div class ="control-group">
                <label for="single_com_u2">u2</label>
                <input type="text" class="form-control" name="single_com_u2[]" >
            </div>
        </div>
    </div>
    </div>
    
    `)
    elem.show();
    $(this).attr('disabled',true);

  });


  

  $(document).on("click",".add_M_com" ,function(){

    var elem = $(this).parent().find(".componentGroup");
 
    elem.append(`  
    <div class="componentItem mb-2">
    <div class="form-group">
        <div class="row p-2">
            <button type="button" class="btn btn-light normal-com col-4 form-control m-2">Normal</button>
            <button type="button" class="btn btn-light uniform-com form-control col-4 form-control m-2">Uniform</button>
        </div>

        <div class="single-com-view"></div>
        <div class="form-group">

        <label for="M_com_weight">Weight:</label>
        <input type="number" step="0.1" class="form-control mb-2" name="M_com_weight[]">
     
        </div>  
    </div>  
    </div>
    `);
    console.log(elem);
    elem.show();
  
  })

  $(document).on("click", "#add_IPV" , function(){

    $('#IPV-group').show();

    var elem = $(this).parent().find("#IPV-group").find(".field-group");
    
    elem.find('.ipt-field').remove();
 
    for(var i=0; i<state; i++){

        elem.append(`<input type="number" class="ipt-field m-2" placeholder="Enter value for state ${i+1}" step="0.1" min="0.0" >`);
    }

  });

  $(document).on("change", ".ipt-field" , function(){
   
    let ipvarr =[];
    ipvarr = $('.ipt-field').map(function(){
        return this.value;
    }).get();
   
    console.log(ipvarr.join(','));
    var s = sum(ipvarr);
    var ele=  document.getElementById('IPV-Value');
    if(s!=1){
     $('#error').show();
     ele.value ="";
    }
    else if(s==1){
        $('#error').hide();
        ele.value ="";
        ele.value = ipvarr.join(',');
    }
        
    


 
  

  });

  function sum(a) {
    return (a.length && parseFloat(a[0]) + sum(a.slice(1))) || 0;
  }


});
