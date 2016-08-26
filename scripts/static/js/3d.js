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

  var numOwls = 5;
  var owlPositions = [
    new THREE.Vector3( 0,  0,  0),
    new THREE.Vector3(-2,  0, -2),
    new THREE.Vector3( 3,  0,  2),
    new THREE.Vector3(-4,  0, -7),
    new THREE.Vector3(-7,  0, -6)
  ];
  var owlCameras = [
    new THREE.Vector3(10, 0, 0),
    new THREE.Vector3(5, 0, -2),
    new THREE.Vector3(10, 4, 0),
    new THREE.Vector3(10, 4, 0),
    new THREE.Vector3(10, 4, 0)
  ];
  var cameraPositionOverview = new THREE.Vector3(10, 4, 0);
  var lookAtOverview = new THREE.Vector3(0, 3.2, 0);
  var cameraPositionTarget = new THREE.Vector3(0, 0, 0);
  var cameraLookAtTarget = new THREE.Vector3(0, 0, 0);

  var owlScales = [1.0, 1.0, .33, .33, .33];
  var owlNames = ['MARTHA', 'KLAUS', 'KEVIN','MAJA','LISA'];
  var owlBounds;

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
    targetAmbients[i] = 0.25;
    targetAmbientsStart[i] = 0.0;
    submitRotations[i] = 0.0;
    submitAmbients[i] = 0.0;
  }


  var raycaster = new THREE.Raycaster();
  var intersects;
  var pointer = new THREE.Vector2();
  var selectedOwl = document.location.hash.substr(1) || 'KLAUS';
  var touchOwl;
  var owlSizes = [];

  container = document.querySelector('.viewport');

  WIDTH = window.innerWidth;
  HEIGHT = window.innerHeight;

  VIEW_ANGLE = 45;
  ASPECT = WIDTH / HEIGHT;
  NEAR = 1;
  FAR = 10000;

  var sio;


  function updateOwl(data) {
    var index, mesh, duration, angle, currentLight;

    if (data.action == 'command' && data.command == 'move') {
      index = owlNames.indexOf(data.name);
      if (index <= 0) return;
      
console.log(index,data.name,owlNames);
      mesh = scene.getObjectByName('HullHead.'+index);
      angle = mesh.rotation.z;

      // targetRotations[index] = data['end_angle'];
      console.log('rotating ',index,' to ', targetRotations[index]);

      turnHead(touchOwl, data['end_angle'], data.duration );

    } else
    if (data.action == 'command' && data.command == 'dim') {

      // index = owlNames.indexOf(data.name);
      // currentLight = targetAmbients[index];
      // targetAmbients[index] = data['end_val'];
    }

  }

  function turnHead(owl, targetAngle, duration) {
      var mesh = scene.getObjectByName('HullHead.'+owl);
      new TWEEN.Tween(mesh.rotation).to({ z: targetAngle }, duration).easing(TWEEN.Easing.Linear.None).start();
  }


  function init() {
    //var websocket;
    //var wsUri = 'ws://' + window.location.host + '/ws';
    //if (window.WebSocket) {
    //  websocket = new WebSocket(websocket);
    //}
    //else if (window.MozWebSocket) {
    //  websocket = MozWebSocket(websocket);
    //}
    //else {
    //  console.log('WebSocket Not Supported');
    //  return;
    //}

    
    var websocket = new WebSocket('ws://' + window.location.host + '/ws');
    websocket.onopen    = function (evt) { console.log("Connected to WebSocket server."); };
    websocket.onclose   = function (evt) { console.log("Disconnected"); };
    websocket.onmessage = function (evt) {
      var msg;
      try {
        msg = JSON.parse(evt.data);
        updateOwl(msg);
      } catch (e) {
        console.error(e);
      }
    };
    websocket.onerror   = function (evt) { console.log('Error occured: ' + evt.data); };


    scene = new THREE.Scene();
    renderer = new THREE.WebGLRenderer({
      antialias: true
    });
    renderer.setSize(WIDTH, HEIGHT);

    // not supported on mobile devices
    //renderer.shadowMap.enabled = false;
    //renderer.shadowMap.soft = true;

    renderer.shadowMap.enabled = false;
    renderer.shadowMap.type = THREE.PCFShadowMap;
    renderer.shadowMap.autoUpdate = true;

    container.appendChild(renderer.domElement);

    camera = new THREE.PerspectiveCamera(VIEW_ANGLE, ASPECT, NEAR, FAR);

    camera.position.set( cameraPositionOverview.x, cameraPositionOverview.y, cameraPositionOverview.z );
    camera.lookAt(lookAtOverview);
    cameraPositionTarget = cameraPositionOverview;
    cameraLookAtTarget = lookAtOverview;

    scene.add(camera);

    light = new THREE.DirectionalLight(0xa7a79e);
    light.position.set(30, 100, 60);
    light.castShadow = false;
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

    ambient = new THREE.AmbientLight(0x444749, 0.1); //0x4c555e
    scene.add(ambient);

    loader = new THREE.ObjectLoader();

    // load the model and create everything
    loader.load('models/snowy-owl.json', function (data) {
      var meshes = {}, i, j, head, body, p, light;
      var sizeHead, sizeBody;

      console.log(data);
      data.children.forEach(function(mesh) {
        meshes[mesh.name] = mesh;
      });

      head = meshes['HullHead'];
      body = meshes['HullBody'];

      head.material.emissiveMap = THREE.ImageUtils.loadTexture('models/emission_head.jpg');
      body.material.emissiveMap = THREE.ImageUtils.loadTexture('models/emission_body.jpg');

      for (i=0; i<owls.length; i++) {
        owls[i].head =  head.clone();
        owls[i].body = body.clone();
        owls[i].head.scale.set(owlScales[i], owlScales[i], owlScales[i]);
        owls[i].body.scale.set(owlScales[i], owlScales[i], owlScales[i]);

        owls[i].head.material = head.material.clone();
        owls[i].body.material = body.material.clone();

        owls[i].head.material.emissive = new THREE.Color(0xFFFFFF);
        owls[i].body.material.emissive = new THREE.Color(0xFFFFFF);

        p = owls[i].head.position.add(owls[i].pos);
        //owls[i].head.position.set(p.x, owlScales[i] * p.y, p.z);
        p = owls[i].body.position.add(owls[i].pos);
        owls[i].body.position.set(p.x, p.y, p.z);

        owls[i].head.name = 'HullHead.'+i;
        owls[i].body.name = 'HullBody.'+i;

        scene.add(owls[i].head);
        scene.add(owls[i].body);


        sizeHead = new THREE.Box3().setFromObject( owls[i].head).size();
        sizeBody = new THREE.Box3().setFromObject( owls[i].body).size();
        owlSizes[i] = [sizeHead.x + sizeBody.x, sizeHead.y + sizeBody.y, sizeHead.z+sizeBody.z];

        //
        // point light for head (left eye, right eye, back of head)
        //
        // light = new THREE.PointLight( 0xff0000, 0.5);
        // light.name = 'light.head.eye_left.'+i;
        // light.position.set( owls[i].head.position.x + sizeHead.x, owls[i].head.position.y + 2*sizeHead.y, owls[i].head.position.z  + sizeHead.z);
        // scene.add( light );

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

  function render(time) {
    var i, owl;
    //var owl = getTargetOwl();

    TWEEN.update(time);

    for (owl = 0; owl<owls.length; owl++) {
      var mesh = scene.getObjectByName('HullHead.'+owl);
      // mesh.rotation.z += ( targetRotations[owl] - mesh.rotation.z ) * 0.05;

      var color = new THREE.Color(targetAmbients[owl], targetAmbients[owl], targetAmbients[owl]);
      mesh.material.emissive = color;
      mesh = scene.getObjectByName('HullBody.'+owl);
      mesh.material.emissive = color;

      submitValuesThrottled(owl, targetRotations[owl], targetAmbients[owl])
    }

    renderer.render(scene, camera);
    requestAnimationFrame(render);
  }

  function tweenCamera(targetPos, targetLookAt) {

    var duration = 1000;
    // see http://stackoverflow.com/questions/15696963/three-js-set-and-read-camera-look-vector/15697227#15697227
    var currentLookAt = new THREE.Vector3( 0, 0, -1 ).applyQuaternion( camera.quaternion ).add( camera.position );

    var camUpdate = function() {
      var v = currentLookAt.clone().add(targetLookAt.clone().sub(currentLookAt).multiplyScalar(this.t));
      camera.lookAt(v);
    };

    var prop = {
      t: 0.0
    };
    new TWEEN.Tween(prop).to({ t: 1.0 }, duration).easing(TWEEN.Easing.Cubic.InOut).onUpdate(camUpdate).start();
  }

  function updateRaycasting() {
    // update raycast
    raycaster.setFromCamera(pointer, camera);
    intersects = raycaster.intersectObjects( scene.children );
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
    var mesh;

    event.preventDefault();
    document.addEventListener( 'mousemove', onDocumentMouseMove, false );
    document.addEventListener( 'mouseup', onDocumentMouseUp, false );
    document.addEventListener( 'mouseout', onDocumentMouseOut, false );
    mouseXStart = event.clientX - centerX;
    mouseYStart = event.clientY;
    pointer.set(( event.clientX / window.innerWidth ) * 2 - 1, - ( event.clientY / window.innerHeight ) * 2 + 1);
    updateRaycasting();

    var owl = getTargetOwl();
    // for (i=0; i<intersects.length; i++) {
    //   console.log(intersects[i]);
    // }

    // zoom in on owl if not yet
    if (typeof owl !== 'undefined' && cameraPositionTarget != owlCameras[owl]) {
      cameraPositionTarget = owlCameras[owl].clone();
      cameraLookAtTarget = owlPositions[owl].clone();
      cameraLookAtTarget.add(new THREE.Vector3(0, owlSizes[owl][1] / 2, 0));
    } else
    if (typeof owl === 'undefined') {
      cameraPositionTarget = cameraPositionOverview;
      cameraLookAtTarget = lookAtOverview;
    }

    tweenCamera(cameraPositionTarget, cameraLookAtTarget);

    if (typeof owl !== 'undefined') {
      touchOwl = owl;
      mesh = scene.getObjectByName('HullHead.'+owl);
      targetRotationsStart[owl] = mesh.rotation.z; //targetRotations[owl];
      targetAmbientsStart[owl] = targetAmbients[owl];
    }

  }

  function onDocumentMouseMove( event ) {
    var mesh;
    var owl = getTargetOwl();

    mouseX = event.clientX - centerX;
    mouseY = event.clientY;
    pointer.set(( event.clientX / window.innerWidth ) * 2 - 1, - ( event.clientY / window.innerHeight ) * 2 + 1);
    updateRaycasting();

    turnHead(touchOwl, clamp(targetRotationsStart[touchOwl] + ( mouseX - mouseXStart ) * 0.01, -Math.PI, 0), 1.0 );
    // targetRotations[owl] = clamp(targetRotationsStart[owl] + ( mouseX - mouseXStart ) * 0.01, -Math.PI, 0);

    targetAmbients[touchOwl] = clamp(targetAmbientsStart[touchOwl] + (mouseYStart - mouseY) * 0.005, 0.0, 1.0);
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
    var mesh;
    var owl = 0;
    if ( event.touches.length === 1 ) {
      owl = getTargetOwl();

      pointer.set(( event.touches[0].pageX / window.innerWidth ) * 2 - 1, - ( event.touches[0].pageY / window.innerHeight ) * 2 + 1);
      updateRaycasting();

      var owl = getTargetOwl();
      for (i=0; i<intersects.length; i++) {
        // console.log(intersects[i]);
      }

      // zoom in on owl if not yet
      if (typeof owl !== 'undefined' && cameraPositionTarget != owlCameras[owl]) {
        cameraPositionTarget = owlCameras[owl].clone();
        cameraLookAtTarget = owlPositions[owl].clone();
        cameraLookAtTarget.add(new THREE.Vector3(0, owlSizes[owl][1] / 2, 0));
      } else
      if (typeof owl === 'undefined') {
        cameraPositionTarget = cameraPositionOverview;
        cameraLookAtTarget = lookAtOverview;
      }

      tweenCamera(cameraPositionTarget, cameraLookAtTarget);

      event.preventDefault();
      mouseXStart = event.touches[0].pageX - centerX;
      mouseYStart = event.touches[0].pageY;

      if (typeof owl !== 'undefined') {
        touchOwl = owl;
        mesh = scene.getObjectByName('HullHead.'+owl);
        console.log('tocuhowl',touchOwl);
        targetRotationsStart[owl] = mesh.rotation.z;
        targetAmbientsStart[owl] = targetAmbients[owl];
      }

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
      updateRaycasting();

      turnHead(touchOwl, clamp(targetRotationsStart[touchOwl] + ( mouseX - mouseXStart ) * 0.01, -Math.PI, 0), 1.0 );
      // targetRotations[owl] = clamp(targetRotationsStart[owl] + ( mouseX - mouseXStart ) * 0.01, -Math.PI, 0);

      targetAmbients[owl] = clamp(targetAmbientsStart[owl] + (mouseYStart - mouseY) * 0.005, 0.0, 1.0);
    }
  }

  init();
  submitValuesThrottled = $.throttle(250, submitValues);
})();
