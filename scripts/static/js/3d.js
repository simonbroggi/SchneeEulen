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
  var WIDTH, HEIGHT, VIEW_ANGLE, VIEW_ANGLE_OVERVIEW, ASPECT, NEAR, FAR;

  var mouseX, mouseY;
  var mouseXStart = 0, mouseYStart = 0;
  var submitValuesThrottled;
  var activeTouchOwl;

  var centerX = window.innerWidth / 2;
  var centerY = window.innerHeight / 2;
  var ambient;

  var owls = [];
  var targetRotations = [], targetAmbients = [];
  var targetRotationsStart = [], targetAmbientsStart = [];
  var submitRotations = [], submitAmbients = [];

  // -z, +y, +x
  var cameraPositionOverview = new THREE.Vector3(28, 8, 0);
  var lookAtOverview = new THREE.Vector3(0, 4, -3);
  var cameraPositionTarget = new THREE.Vector3(0, 0, 0);
  var cameraLookAtTarget = new THREE.Vector3(0, 0, 0);
  var cameraTarget, cameraOverview;

  // owl camera settings
  VIEW_ANGLE_OVERVIEW = 70;
  VIEW_ANGLE = 45;
  ASPECT = WIDTH / HEIGHT;
  NEAR = 1;
  FAR = 10000;

  // look at factor * owlHeight
  var cameraLookAtHeight = 0.4;


  var owlScales = [1.0, 1.0, .5, .5, .5];
  var owlNames = ['KLAUS', 'MARTHA', 'KEVIN','MAJA','LISA'];
  var owlBounds;

  var numOwls = 5;
   // -z, +y, +x
  var owlPositions = [
    new THREE.Vector3( -2,  4,  -1),
    new THREE.Vector3(4,  0, -8),
    new THREE.Vector3( -2,  4,  4),
    new THREE.Vector3(0,  1, 2),
    new THREE.Vector3(-1, 2, -5)
  ];
  var owlCameras = [
    new THREE.Vector3(10, 10, 0),
    new THREE.Vector3(14, 2, -6),
    new THREE.Vector3(7, 4, 10),
    new THREE.Vector3(8, 3, 4),
    new THREE.Vector3(10, 3, 0)
  ];


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

  var websocket;
  var timerId;

  container = document.querySelector('.viewport');

  WIDTH = window.innerWidth;
  HEIGHT = window.innerHeight;


  var sio;
  var tsRot = -1, tsDimBody = -1;

  function initWebsockets() {
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

    var onWebsocketOpen = function (evt) {
      console.log("Connected to WebSocket server.");

      if (timerId) {
        clearInterval(timerId);
        timerId = undefined;
      }
    };

    var onWebsocketClose = function (evt) {
      console.log("Websocket disconnected");
      websocket = undefined;

      reconnect();
    };

    var onWebsocketMessage = function (evt) {
      var msg;

      // parse message
      try {
        if (typeof evt.data !== 'undefined') {
          evt.data.replace(/nan/g,/\"NaN\"/);
        }

        if (evt.data === '') {
          return;
        }

        // console.log(evt.data, evt.data.indexOf('{'));

        if (evt.data.indexOf('{') === 0) {
          msg = JSON.parse(evt.data);

          // ensure consistency / prepare numbers
          if (msg.end_val) msg.end_val = +msg.end_val;
          if (msg.start_val) msg.start_val = +msg.start_val;
          if (msg.duration) msg.duration = +msg.duration;
          if (msg.end_angle) msg.end_angle = -1 * (+msg.end_angle);

          // console.log(msg);
          externalUpdateHandler(msg);
        } else {
          console.info(evt, evt.data);
        }

      } catch (e) {
        console.error(e);
      }
    };

    var onWebsocketError = function (evt) {
      console.error('Websocket error occured: ', evt.data, timerId);
      websocket = undefined;
    };

    var reconnect = function() {
      console.log('reconnect timer',timerId,'websocket',websocket);
      if (!websocket) {
        try {
          websocket = new WebSocket('ws://' + window.location.host + '/ws');
          websocket.onclose = onWebsocketClose;
          websocket.onopen = onWebsocketOpen;
          websocket.onmessage = onWebsocketMessage;
          websocket.onerror = onWebsocketError;

          console.log('created new websocket',websocket);
        } catch (e) {
          console.error(e);
          websocket = undefined;
        }
      }

      if (!websocket) {
        console.log('no websocket',websocket);
        if (timerId) {
          clearInterval(timerId);
          timerId = undefined;
        }
        timerId = setInterval(this, 3000);
      }
    };

    // init websockets on page load
    reconnect();
  }

  /**
   * Update owl state (rotation, lighting)
   * @param data
   */
  function externalUpdateHandler(data) {
    var index, mesh, duration, angle, currentLight;

    if (typeof data === 'undefined') return;

    if (data.action == 'command' && data.command == 'move') {
      data.clients.forEach(function(val, index) {
        index = owlNames.indexOf(val);

        mesh = scene.getObjectByName('HullHead.'+index);
        angle = mesh.rotation.z;

        var rad = Math.PI * data['end_angle']/180;

        console.log('-> incoming angle', data['end_angle'], '('+rad+') rad', ' current = ', mesh.rotation.z);

        // note: due to the implementation of multi-threading at the cherrypy/ws4py server side, commands
        // may arrive in wrong order! We therefore use a pre-command timestamp to ignore older packets
        if (data.ts <= tsRot) console.error(data);
        if (index !== +activeTouchOwl && data.ts > tsRot) {
          tsRot = data.ts;

          turnHead(index, -Math.PI - rad, data.duration, false );
          console.log('[websocket update] rotating ', val,'('+index+')',' to ', data['end_angle'], '('+rad+')', 'in', data.duration,'ts=',data.ts);

        }
      });
    } else
    if (data.action == 'command' && data.command == 'dim') {
      data.clients.forEach(function(val, index) {
        index = owlNames.indexOf(val);

        if (data.id == 'body' && index !== +activeTouchOwl && data.ts > tsDimBody) {
          tsDimBody = data.ts;
          currentLight = targetAmbients[index];
          console.log('[websocket update] dim ', val,'('+index+'):', data.id,' to ', data['end_val'], 'in', data.duration,'ts=',data.ts);
          targetAmbients[index] = data['end_val'];
        }
      })
    }
  }

  function turnHead(owl, targetAngle, duration, send) {
    var mesh = scene.getObjectByName('HullHead.'+owl);
    new TWEEN.Tween(mesh.rotation).to({ z: targetAngle }, duration).easing(TWEEN.Easing.Linear.None).start();

    if (send) {
      submitValuesThrottled(owl, targetAngle, targetAmbients[owl])
    }
  }


  function submitValues(owl, newValueRot, newValueAmbient) {
    if (newValueRot != submitRotations[owl] || newValueAmbient != submitAmbients[owl]) {
      console.log('send values owl',owl,'rot',(180.0/Math.PI) * newValueRot,'('+newValueRot+')','light',newValueAmbient);

      var deg = 180.0 + (180.0/Math.PI) * newValueRot;
      console.log('submit angle',deg);
      var cmd = 'send/' + owlNames[owl] + '/' + deg + '/' + newValueAmbient;

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

  // see http://youmightnotneedjquery.com/
  function toggleClass(el, className) {
    if (el === null) { return; }
    if (el.classList) {
      el.classList.toggle(className);
    } else {
      var classes = el.className.split(' ');
      var existingIndex = classes.indexOf(className);

      if (existingIndex >= 0) {
        classes.splice(existingIndex, 1);
      } else {
        classes.push(className);
      }
      el.className = classes.join(' ');
    }
  }

  function addClass(el, className) {
    if (el === null) { return; }
    if (el.classList) {
      el.classList.add(className);
    } else {
      el.className += ' ' + className;
    }
  }

  function removeClass(el, className) {
    if (el === null) { return; }
    if (el.classList) {
      el.classList.remove(className);
    } else {
      el.className = el.className.replace(new RegExp('(^|\\b)' + className.split(' ').join('|') + '(\\b|$)', 'gi'), ' ');
    }
  }

  /**
   * Init 3d owl interface.
   */
  function init() {

    initWebsockets();

    scene = new THREE.Scene();
    renderer = new THREE.WebGLRenderer({
      antialias: true
    });
    scene.background = new THREE.Color( 0x000000 );
    renderer.setSize(WIDTH, HEIGHT);

    // not supported on mobile devices
    //renderer.shadowMap.enabled = false;
    //renderer.shadowMap.soft = true;

    renderer.shadowMap.enabled = false;
    renderer.shadowMap.type = THREE.PCFShadowMap;
    renderer.shadowMap.autoUpdate = true;

    container.appendChild(renderer.domElement);

    // map owl cameras
    var mappedCameras = owlCameras.map(function(v, i) {
      var cam = new THREE.PerspectiveCamera(VIEW_ANGLE, ASPECT, NEAR, FAR);
      cam.position.copy(v);
      return cam;
    });
    owlCameras = mappedCameras;

    camera = new THREE.PerspectiveCamera(VIEW_ANGLE, ASPECT, NEAR, FAR);
    cameraOverview = camera;

    camera.position.set( cameraPositionOverview.x, cameraPositionOverview.y, cameraPositionOverview.z );
    camera.lookAt(lookAtOverview);
    cameraOverview = camera.clone();

    // cameraPositionTarget = cameraPositionOverview;
    // cameraLookAtTarget = lookAtOverview;

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
    loader.load('static/models/snowy-owl-improved.json', function (data) {
      var meshes = {}, i, j, head, body, p, light;
      var sizeHead, sizeBody;

      data.children.forEach(function(mesh) {
        meshes[mesh.name] = mesh;
      });

      head = meshes['HullHead'];
      body = meshes['HullBody'];

      head.material.emissiveMap = THREE.ImageUtils.loadTexture('static/models/emission_head.jpg');
      body.material.emissiveMap = THREE.ImageUtils.loadTexture('static/models/emission_body.jpg');

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

        // initial head rotation: 90°
        owls[i].head.rotateZ(-Math.PI/2);

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

      // look at owls
      owlCameras.forEach(function(v, i) {
        var p = owlPositions[i].add(new THREE.Vector3(0, owlSizes[i][1]*cameraLookAtHeight, 0));
        v.lookAt(p);
      });

      render();
    });

    // see https://github.com/mrdoob/three.js/blob/master/examples/canvas_geometry_cube.html
    window.addEventListener( 'resize', onWindowResize, false );
    document.addEventListener( 'mousedown', onDocumentMouseDown, false );
    document.addEventListener( 'touchstart', onDocumentTouchStart, false );
    document.addEventListener( 'touchmove', onDocumentTouchMove, false );
    document.addEventListener('touchend', onDocumentTouchEnd, false);

    document.getElementById('back').addEventListener('click', onBackButtonClick);
  }

  function onBackButtonClick() {
    cameraTarget = cameraOverview;
    tweenCamera(cameraOverview);
    touchOwl = undefined;
    activeTouchOwl = undefined;
    
    setUIOverview();
  }

  function setUIOverview() {
    addClass(document.querySelector('.instructions-owl'), 'invisible');
    removeClass(document.querySelector('.instructions-overview'), 'invisible');
    removeClass(document.querySelector('h1'), 'invisible');
    removeClass(document.getElementById('back'), 'owl');
  }

  function setUIFocus(owl) {
    addClass(document.getElementById('back'), 'owl');
    addClass(document.querySelector('.instructions-overview'), 'invisible');
    removeClass(document.querySelector('.instructions-owl'), 'invisible');
    addClass(document.querySelector('h1'), 'invisible');
  }

  function hideUIInstructions() {
    addClass(document.querySelector('.instructions-owl'), 'invisible');
    addClass(document.querySelector('.instructions-overview'), 'invisible');
    addClass(document.querySelector('h1'), 'invisible');
  }

  function clamp(x, a, b) {
    return Math.max(a, Math.min(x, b));
  }

  /**
   * Global render loop
   * @param time
   */
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
    }

    renderer.render(scene, camera);
    requestAnimationFrame(render);
  }

  /**
   * Focus on one owl, using camera tweening
   * @param targetPos
   * @param targetLookAt
     */
  function tweenCamera(targetCamera) {

    var duration = 500;

    // see http://stackoverflow.com/questions/15696963/three-js-set-and-read-camera-look-vector/15697227#15697227
    // var currentLookAt = new THREE.Vector3( 0, 0, -1 ).applyQuaternion( camera.quaternion ).add( camera.position );
    // var currentPos = camera.position.clone();
    //
    // var camUpdate = function() {
    //   var v = currentLookAt.clone().add(targetLookAt.clone().sub(currentLookAt).multiplyScalar(this.t));
    //   camera.position.copy( currentPos.clone().add(targetPos.clone().sub(currentPos).multiplyScalar(this.t)) );
    //   camera.lookAt(v);
    // };
    //
    // var prop = {
    //   t: 0.0
    // };
    // new TWEEN.Tween(prop).to({ t: 1.0 }, duration).easing(TWEEN.Easing.Cubic.InOut).onUpdate(camUpdate).start();

    var fromQuaternion = camera.quaternion.clone();
    var fromPosition = camera.position.clone();
    var camUpdate = function(t) {
      camera.quaternion.copy(fromQuaternion).slerp(targetCamera.quaternion, t);
      camera.position.copy(fromPosition).lerp(targetCamera.position, t);
    };

    var prop = {
      t: 0.0
    };
    new TWEEN.Tween(prop).to({ t: 1.0 }, duration).onUpdate(camUpdate).start();
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

  /**
   * Returns the first owl matching the raycast intersects.
   * @returns {*}
     */
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

    // zoom in on owl if not yet
    if (typeof owl !== 'undefined' && cameraTarget != owlCameras[owl]) {
      cameraTarget = owlCameras[owl];
      setUIFocus(owl);
    } else if (typeof owl === 'undefined') {
      if (typeof touchOwl === 'undefined') {
        cameraTarget = cameraOverview;
        setUIOverview();
      } else {
        owl = touchOwl;
      }
    }

    tweenCamera(cameraTarget);

    if (typeof owl !== 'undefined') {
      touchOwl = owl;
      mesh = scene.getObjectByName('HullHead.'+owl);
      targetRotationsStart[owl] = mesh.rotation.z; //targetRotations[owl];
      targetAmbientsStart[owl] = targetAmbients[owl];
    } else {
      touchOwl = undefined;
    }
  }

  function onDocumentMouseMove( event ) {
    var mesh;

    hideUIInstructions();
    mouseX = event.clientX - centerX;
    mouseY = event.clientY;
    pointer.set(( event.clientX / window.innerWidth ) * 2 - 1, - ( event.clientY / window.innerHeight ) * 2 + 1);
    updateRaycasting();

    var owl = getTargetOwl() || touchOwl;
    if (typeof owl !== 'undefined') {
      activeTouchOwl = touchOwl;
      turnHead(touchOwl, clamp(targetRotationsStart[touchOwl] + ( mouseX - mouseXStart ) * 0.01, -Math.PI, 0), 1.0, true );
      targetAmbients[touchOwl] = clamp(targetAmbientsStart[touchOwl] + (mouseYStart - mouseY) * 0.005, 0.0, 1.0);
    }
  }

  function onDocumentMouseUp( event ) {
    document.removeEventListener( 'mousemove', onDocumentMouseMove, false );
    document.removeEventListener( 'mouseup', onDocumentMouseUp, false );
    document.removeEventListener( 'mouseout', onDocumentMouseOut, false );
    // touchOwl = undefined;
  }

  function onDocumentMouseOut( event ) {
    document.removeEventListener( 'mousemove', onDocumentMouseMove, false );
    document.removeEventListener( 'mouseup', onDocumentMouseUp, false );
    document.removeEventListener( 'mouseout', onDocumentMouseOut, false );
    activeTouchOwl = touchOwl;
  }

  function onDocumentTouchStart( event ) {
    var mesh;
    var owl = 0;
    if ( event.touches.length === 1 ) {
      owl = getTargetOwl();

      pointer.set(( event.touches[0].pageX / window.innerWidth ) * 2 - 1, - ( event.touches[0].pageY / window.innerHeight ) * 2 + 1);
      updateRaycasting();

      var owl = getTargetOwl();

      // zoom in on owl if not yet
      if (typeof owl !== 'undefined' && cameraTarget != owlCameras[owl]) {
        cameraTarget = owlCameras[owl];
        setUIFocus(owl);
      } else if (typeof owl === 'undefined') {
        if (typeof touchOwl === 'undefined') {
          cameraTarget = cameraOverview;
          setUIOverview();
        } else {
          owl = touchOwl;
        }
      }

      tweenCamera(cameraTarget);

      // event.preventDefault();
      mouseXStart = event.touches[0].pageX - centerX;
      mouseYStart = event.touches[0].pageY;

      if (typeof owl !== 'undefined') {
        touchOwl = owl;
        mesh = scene.getObjectByName('HullHead.'+owl);
        targetRotationsStart[owl] = mesh.rotation.z;
        targetAmbientsStart[owl] = targetAmbients[owl];
      } else {
        touchOwl = undefined;
      }

    }
  }

  function onDocumentTouchMove( event ) {
    if ( event.touches.length === 1 ) {

      event.preventDefault();
      mouseX = event.touches[0].pageX - centerX;
      mouseY = event.touches[0].pageY;

      pointer.set(( event.touches[0].pageX / window.innerWidth ) * 2 - 1, - ( event.touches[0].pageY / window.innerHeight ) * 2 + 1);
      updateRaycasting();

      var owl = getTargetOwl() || touchOwl;
      if (typeof touchOwl !== 'undefined') {
        activeTouchOwl = touchOwl;
        hideUIInstructions();
        turnHead(touchOwl, clamp(targetRotationsStart[touchOwl] + ( mouseX - mouseXStart ) * 0.01, -Math.PI, 0), 1.0, true );
        targetAmbients[touchOwl] = clamp(targetAmbientsStart[touchOwl] + (mouseYStart - mouseY) * 0.005, 0.0, 1.0);
      }

    }
  }

  function onDocumentTouchEnd(event) {
    activeTouchOwl = undefined;
  }

  init();
  submitValuesThrottled = $.throttle(250, submitValues);

  // special UI hooks

})();
