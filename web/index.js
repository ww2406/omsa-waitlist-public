const app = new Vue({
    el: '#app',
    data: {
        courses: [],
        dept: 'all'
    },
    computed: {
        fullWaitlistCourses: function () {
            let wlc = this.courses.filter(x => x.wl_remaining <= 0);
            if (this.dept !== 'all') {
                wlc = wlc.filter(x => x.dept === this.dept);
            }
            return wlc;
        },
        notFullWaitlistCourses: function () {
            let wlc = this.courses.filter(x => x.wl_remaining > 0);
            if (this.dept !== 'all') {
                wlc = wlc.filter(x => x.dept === this.dept);
            }
            return wlc;
        }
    },
    methods: {
        subscribeToCourse: function (crn) {
            messaging.requestPermission().then(() => {
                console.log('Permission granted');
                messaging.getToken({vapidKey: 'BGnPYb2DFQd5dCYzopluHIVWrbf3EWVSNtmLSvvhiFF8ungvmbpE-eGP6JZ0mSBO0DOGCzTj15-t1JmwSgkFKQ0'})
                    .then(currentToken => {
                        let data = {
                            token: currentToken,
                            crn: crn,
                            term: '202108'
                        };
                        fetch('https://us-central1-omsawaitlist.cloudfunctions.net/subscribe',{
                            method: 'POST',
                            headers: {
                                'Content-Type': 'application/json'
                            },
                            body: JSON.stringify(data)
                        }).then(() => console.log('subscribed'))
                            .catch(err => console.error(err));
                    })
            }).catch(() => {
                alert('To alert you when a space on the waitlist opens, we need permission to send notifications.');
            })
        }
    }
});

messaging.onMessage((payload) => {
    console.log(payload);
});