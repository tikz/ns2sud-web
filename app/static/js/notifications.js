'use strict';

var applicationServerPublicKey = 'BKnQJXUb4N0EuGGZ-Ui-tS3AdAvYWfgcCp5YM0vNc_v9opYXvip8b_xpthNUmaDK0xIQT7nPrRjifXCwNR3lg60';

const pushButton = document.querySelector('#notifications-toggle');

let isSubscribed = false;
let swRegistration = null;

function urlB64ToUint8Array(base64String) {
  const padding = '='.repeat((4 - base64String.length % 4) % 4);
  const base64 = (base64String + padding)
    .replace(/\-/g, '+')
    .replace(/_/g, '/');

  const rawData = window.atob(base64);
  const outputArray = new Uint8Array(rawData.length);

  for (let i = 0; i < rawData.length; ++i) {
    outputArray[i] = rawData.charCodeAt(i);
  }
  return outputArray;
}

function updateBtn() {
  if (Notification.permission === 'denied') {
    pushButton.textContent = 'Push Messaging Blocked.';
    pushButton.disabled = true;
    updateSubscriptionOnServer(null);
    return;
  }

  if (isSubscribed) {
    pushButton.checked = true;
  } else {
    pushButton.checked = false;
  }
}

function updateSubscriptionOnServer(subscription) {
  axios.post('/notifications/subscribe', subscription).then(function () {
    pushButton.disabled = false;
  });
}

function removeSubscriptionOnServer(subscription) {
  axios.post('/notifications/unsubscribe', subscription).then(function () {
    pushButton.disabled = false;
  });
}

function subscribeUser() {
  pushButton.disabled = true;
  const applicationServerKey = urlB64ToUint8Array(applicationServerPublicKey);
  swRegistration.pushManager.subscribe({
    userVisibleOnly: true,
    applicationServerKey: applicationServerKey
  })
    .then(function (subscription) {

      updateSubscriptionOnServer(subscription);

      isSubscribed = true;

      updateBtn();
    });
}

function unsubscribeUser() {
  pushButton.disabled = true;
  swRegistration.pushManager.getSubscription()
    .then(function (subscription) {
      removeSubscriptionOnServer(subscription);
      if (subscription) {
        return subscription.unsubscribe();
      }
    })
    .then(function () {

      isSubscribed = false;

      updateBtn();
    });
}

function initializeUI() {
  pushButton.addEventListener('click', function () {
    if (isSubscribed) {
      unsubscribeUser();
    } else {
      subscribeUser();
    }
  });

  swRegistration.pushManager.getSubscription()
    .then(function (subscription) {
      isSubscribed = !(subscription === null);

      updateSubscriptionOnServer(subscription);

      updateBtn();
    });
}

if ('serviceWorker' in navigator && 'PushManager' in window) {
  navigator.serviceWorker.register('sw.js')
    .then(function (swReg) {

      swRegistration = swReg;
      initializeUI();
    });
} else {
  pushButton.textContent = 'Push Not Supported';
}
