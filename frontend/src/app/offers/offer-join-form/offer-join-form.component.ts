import {Component, OnInit} from '@angular/core';
import {FormBuilder, FormGroup, Validators} from '@angular/forms';
import {HttpClient} from '@angular/common/http';
import {Location} from '@angular/common'

import {ActivatedRoute} from '@angular/router';
import {AuthService} from '../../auth.service';
import {OffersService} from 'app/homepage-offer/offers.service';
import {User} from '../../user';
import {UserService} from '../../user.service';

@Component({
  selector: 'volontulo-offer-join-form',
  templateUrl: './offer-join-form.component.html'
})

export class OfferJoinFormComponent implements OnInit {
  public joinForm: FormGroup = this.fb.group({
    applicant_email: [''],
    applicant_name: [''],
    message: ['', [Validators.minLength(10), Validators.maxLength(2000)]],
    phone_no: [''],
  });

  public submitEnabled = false;
  public success: null | boolean = null;
  public offerId: number;
  public error;

  constructor(
    private activatedRoute: ActivatedRoute,
    private fb: FormBuilder,
    private authService: AuthService,
    private userService: UserService,
    private httpClient: HttpClient,
    private offersService: OffersService,
    private location: Location ,
  ) {
  }

  ngOnInit() {
    this.authService.user$
      .subscribe(
        (user: User) => {
          this.joinForm.controls.applicant_email.setValue(user.email);
          this.joinForm.controls.applicant_name.setValue(this.userService.getFullName(user));
          this.joinForm.controls.phone_no.setValue(user.phoneNo);
        }
      );

    this.activatedRoute.params
      .switchMap(params => this.offerId = params.offerId)
      .subscribe()
  }

  onSubmit() {
    if (this.joinForm.valid) {
      this.submitEnabled = true;

      this.offersService.joinOffer(this.offerId, this.joinForm.value.message).subscribe(
        response => {
          if (response.status === 201) {
            this.location.back()}}
      )
    }
  }
}
