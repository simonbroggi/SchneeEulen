/*
 * jQuery throttle / debounce - v1.1 - 3/7/2010
 * http://benalman.com/projects/jquery-throttle-debounce-plugin/
 *
 * Copyright (c) 2010 "Cowboy" Ben Alman
 * Dual licensed under the MIT and GPL licenses.
 * http://benalman.com/about/license/
 */
(function(b,c){var $=b.jQuery||b.Cowboy||(b.Cowboy={}),a;$.throttle=a=function(e,f,j,i){var h,d=0;if(typeof f!=="boolean"){i=j;j=f;f=c}function g(){var o=this,m=+new Date()-d,n=arguments;function l(){d=+new Date();j.apply(o,n)}function k(){h=c}if(i&&!h){l()}h&&clearTimeout(h);if(i===c&&m>e){l()}else{if(f!==true){h=setTimeout(i?k:l,i===c?e-m:e)}}}if($.guid){g.guid=j.guid=j.guid||$.guid++}return g};$.debounce=function(d,e,f){return f===c?a(d,e,false):a(d,f,e!==false)}})(this);
;(function() {
  'use strict';

  var container, scene, renderer, camera, light, cube, loader, animation;
  var WIDTH, HEIGHT, VIEW_ANGLE, ASPECT, NEAR, FAR;

  var mouseX, mouseY;
  var mouseXStart = 0, mouseYStart = 0;
  var submitValuesThrottled;

  //var targetRotationStart = 0, targetRotation = 0;
  //var targetAmbientStart = 0.0, targetAmbient = 0.5;

  var centerX = window.innerWidth / 2;
  var centerY = window.innerHeight / 2;
  var ambient;

  var owls = [];
  var targetRotations = [], targetAmbients = [];
  var targetRotationsStart = [], targetAmbientsStart = [];
  var submitRotations = [], submitAmbients = [];

  var numOwls = 1;
  var owlPositions = [
    new THREE.Vector3( 0,  0,  0),
    new THREE.Vector3(-2,  0, -2),
    new THREE.Vector3( 3,  0,  2),
    new THREE.Vector3(-4,  0, -4),
    new THREE.Vector3(-5,  0, -6)
  ];
  var owlScales = [1.0, 1.0,.33,.33,.33];
  var owlNames = ['MARTHA', 'KLAUS', 'KEVIN','MAJA','LISA'];

  // initialize owl structs
  var i;
  for (i=0; i<numOwls; i++) {
    owls[i] = {
      pos: owlPositions[i],
      name: owlNames[i],
      scale: owlScales[i]
    };

    targetRotations[i] = 0.0;
    targetRotationsStart[i] = 0.0;
    targetAmbients[i] = 0.5;
    targetAmbientsStart[i] = 0.0;
    submitRotations[i] = 0.0;
    submitAmbients[i] = 0.0;
  }


  var raycaster = new THREE.Raycaster();
  var intersects;
  var pointer = new THREE.Vector2();
  var selectedOwl = document.location.hash.substr(1) || 'KLAUS';

  container = document.querySelector('.viewport');

  WIDTH = window.innerWidth;
  HEIGHT = window.innerHeight;

  VIEW_ANGLE = 45;
  ASPECT = WIDTH / HEIGHT;
  NEAR = 1;
  FAR = 10000;


  function init() {

    scene = new THREE.Scene();
    renderer = new THREE.WebGLRenderer({
      antialias: true
    });
    renderer.setSize(WIDTH, HEIGHT);
    renderer.shadowMap.enabled = true;
    renderer.shadowMap.soft = true;
    renderer.shadowMap.type = THREE.PCFShadowMap;
    renderer.shadowMap.autoUpdate = true;

    container.appendChild(renderer.domElement);

    camera = new THREE.PerspectiveCamera(VIEW_ANGLE, ASPECT, NEAR, FAR);
    camera.position.set(10,4,0);
    camera.lookAt(new THREE.Vector3(0, 3.2, 0));
    scene.add(camera);

    light = new THREE.DirectionalLight(0xAAAAAA);
    light.position.set(20, 100, 60);
    light.castShadow = true;
    light.shadow.cameraLeft = -60;
    light.shadow.cameraTop = -60;
    light.shadow.cameraRight = 60;
    light.shadow.cameraBottom = 60;
    light.shadow.cameraNear = 1;
    light.shadow.cameraFar = 1000;
    light.shadow.bias = -.0001;
    light.shadow.mapWidth = light.shadow.mapSize.height = 1024;
    light.shadow.darkness = .7;
    scene.add(light);

    ambient = new THREE.AmbientLight(0x444444);
    scene.add(ambient);

    loader = new THREE.ObjectLoader();

    // load the model and create everything
    loader.load('models/snowy-owl.json', function (data) {
      var meshes = {}, i, head, body, p, light;
      data.children.forEach(function(mesh) {
        meshes[mesh.name] = mesh;
        //console.log(mesh);
      });

      head = meshes['HullHead'];
      body = meshes['HullBody'];

      for (i=0; i<owls.length; i++) {
        owls[i].head =  head.clone();
        owls[i].body = body.clone();
        owls[i].head.scale.set(owlScales[i], owlScales[i], owlScales[i]);
        owls[i].body.scale.set(owlScales[i], owlScales[i], owlScales[i]);

        p = owls[i].head.position.add(owls[i].pos);
        owls[i].head.position.set(p.x, owlScales[i] * p.y, p.z);
        p = owls[i].body.position.add(owls[i].pos);
        owls[i].body.position.set(p.x, p.y, p.z);



        owls[i].head.name = 'HullHead.'+i;
        owls[i].body.name = 'HullBody.'+i;

        scene.add(owls[i].head);
        scene.add(owls[i].body);

        // point light for body
        light = new THREE.PointLight( 0xfffeff, .5, 5 );
        light.name = 'light.body.1-'+i;
        light.position.set( owls[i].body.position.x+2.0, owls[i].body.position.y + 2.5, owls[i].body.position.z );
        scene.add( light );

        // point light for head
        light = new THREE.PointLight( 0xfffeff, .5, 2 );
        light.name = 'light.head.'+i;
        light.position.set( owls[i].head.position.x+2.0, owls[i].head.position.y+1.0, owls[i].head.position.z );
        //scene.add( light );

        onWindowResize();
      }

      //var newHead = meshes[0].clone();
      //newHead.position.set(4, 0, 0);
      //scene.add(newHead);

      //var material = new THREE.MultiMaterial( materials );
      //var mesh = new THREE.Mesh( geometry, material );

      //var bounds = new THREE.Box3().setFromObject( mesh );
      //var maxDim = Math.max(w, h);
      //var aspectRatio = w / h;
      //var distance = maxDim/ 2 /  aspectRatio / Math.tan(Math.PI * fov / 360);

      render();
    });

    // see https://github.com/mrdoob/three.js/blob/master/examples/canvas_geometry_cube.html
    window.addEventListener( 'resize', onWindowResize, false );
    document.addEventListener( 'mousedown', onDocumentMouseDown, false );
    document.addEventListener( 'touchstart', onDocumentTouchStart, false );
    document.addEventListener( 'touchmove', onDocumentTouchMove, false );
  }

  //function raycastOwl(v) {
  //
  //  owls.forEach(function(owl) {
  //    console.log(owl);
  //  });
  //}

  function submitValues(owl, newValueRot, newValueAmbient) {
    if (newValueRot != submitRotations[i] || newValueAmbient != submitAmbients[i]) {
      //console.log('submit rotations',i,newValueRot);
      var deg = (180.0/Math.PI) * newValueRot;
      var cmd = 'send/' + selectedOwl + '/' + deg + '/' + newValueAmbient;

      submitRotations[i] = newValueRot;
      submitAmbients[i] = newValueAmbient;

      //console.log('throttled');
      $.ajax({
        type: 'POST',
        url: '/api/' + cmd,
        data: '{}',
        success: function(data) {},
        contentType: "application/json",
        dataType: 'json'
      });

    }
  }

  function clamp(x, a, b) {
    return Math.max(a, Math.min(x, b));
  }

  function render() {
    var i, owl;
    //var owl = getTargetOwl();

    for (owl = 0; owl<owls.length; owl++) {
      var mesh = scene.getObjectByName('HullHead.'+owl);
      mesh.rotation.z += ( targetRotations[owl] - mesh.rotation.z ) * 0.05;

      var light = scene.getObjectByName('light.body.1-'+owl);
      //light.intensity = targetAmbients[owl] * 1.5;

      light = scene.getObjectByName('light.head.'+owl);
      //light.intensity = targetAmbients[owl] * 1.5;

      mesh.material.color.setRGB(targetAmbients[owl], targetAmbients[owl], targetAmbients[owl]);
      mesh = scene.getObjectByName('HullBody.'+owl);
      mesh.material.color.setRGB(targetAmbients[owl], targetAmbients[owl], targetAmbients[owl]);

      ambient.color.setRGB(targetAmbients[owl]/2 + 0.2, targetAmbients[owl]/2 + 0.2, targetAmbients[owl]/2  + 0.2);

      submitValuesThrottled(owl, targetRotations[owl], targetAmbients[owl])
    }

    // update raycast
    raycaster.setFromCamera(pointer, camera);
    intersects = raycaster.intersectObjects( scene.children );

    renderer.render(scene, camera);
    requestAnimationFrame(render);
  }


  function onWindowResize() {
    centerX = window.innerWidth / 2;
    centerY = window.innerHeight / 2;
    camera.aspect = window.innerWidth / window.innerHeight;
    camera.updateProjectionMatrix();
    renderer.setSize( window.innerWidth, window.innerHeight );
  }

  function getTargetOwl() {
    var i;
    var d = Number.POSITIVE_INFINITY;
    var target;
    if (!intersects) return -1;

    for (i=0; i<intersects.length; i++) {
      intersects[i].object.material.color.set(0xffffff);
      if (intersects[i].object.position.x < d) {
        target = intersects[i].object.name.replace(/.*?\.(\d+)/, '$1');
        d = owls[target].pos;
      }
    }

    //console.log(target);
    return target;
  }

  function onDocumentMouseDown( event ) {
    event.preventDefault();
    document.addEventListener( 'mousemove', onDocumentMouseMove, false );
    document.addEventListener( 'mouseup', onDocumentMouseUp, false );
    document.addEventListener( 'mouseout', onDocumentMouseOut, false );
    mouseXStart = event.clientX - centerX;
    mouseYStart = event.clientY;
    pointer.set(( event.clientX / window.innerWidth ) * 2 - 1, - ( event.clientY / window.innerHeight ) * 2 + 1);

    var owl = getTargetOwl();
    targetRotationsStart[owl] = targetRotations[owl];
    targetAmbientsStart[owl] = targetAmbients[owl];
  }

  function onDocumentMouseMove( event ) {
    var owl = getTargetOwl();

    mouseX = event.clientX - centerX;
    mouseY = event.clientY;
    pointer.set(( event.clientX / window.innerWidth ) * 2 - 1, - ( event.clientY / window.innerHeight ) * 2 + 1);

    targetRotations[owl] = clamp(targetRotationsStart[owl] + ( mouseX - mouseXStart ) * 0.01, -Math.PI, 0);
    targetAmbients[owl] = clamp(targetAmbientsStart[owl] + (mouseYStart - mouseY) * 0.005, 0.0, 1.0);
  }

  function onDocumentMouseUp( event ) {
    document.removeEventListener( 'mousemove', onDocumentMouseMove, false );
    document.removeEventListener( 'mouseup', onDocumentMouseUp, false );
    document.removeEventListener( 'mouseout', onDocumentMouseOut, false );
  }

  function onDocumentMouseOut( event ) {
    document.removeEventListener( 'mousemove', onDocumentMouseMove, false );
    document.removeEventListener( 'mouseup', onDocumentMouseUp, false );
    document.removeEventListener( 'mouseout', onDocumentMouseOut, false );
  }

  function onDocumentTouchStart( event ) {
    var owl = 0;
    if ( event.touches.length === 1 ) {
      owl = getTargetOwl();

      event.preventDefault();
      mouseXStart = event.touches[0].pageX - centerX;
      mouseYStart = event.touches[0].pageY;

      pointer.set(( event.touches[0].pageX / window.innerWidth ) * 2 - 1, - ( event.touches[0].pageY / window.innerHeight ) * 2 + 1);

      targetRotationsStart[owl] = targetRotations[owl];
      targetAmbientsStart[owl] = targetAmbients[owl];
    }
  }

  function onDocumentTouchMove( event ) {
    var owl = 0;
    if ( event.touches.length === 1 ) {
      owl = getTargetOwl();
      event.preventDefault();
      mouseX = event.touches[0].pageX - centerX;
      mouseY = event.touches[0].pageY;

      pointer.set(( event.touches[0].pageX / window.innerWidth ) * 2 - 1, - ( event.touches[0].pageY / window.innerHeight ) * 2 + 1);

      targetRotations[owl] = clamp(targetRotationsStart[owl] + ( mouseX - mouseXStart ) * 0.01, -Math.PI, 0);
      targetAmbients[owl] = clamp(targetAmbientsStart[owl] + (mouseYStart - mouseY) * 0.005, 0.0, 1.0);
    }
  }

  init();
  submitValuesThrottled = $.throttle(250, submitValues);
})();
