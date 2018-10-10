import { Component, OnInit } from '@angular/core';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';
import { HttpClient } from '@angular/common/http';
import { Location } from '@angular/common'

import { ActivatedRoute } from '@angular/router';
import { AuthService } from '../../auth.service';
import { OffersService } from 'app/homepage-offer/offers.service';
import { User } from '../../user';
import { UserService } from '../../user.service';

@Component({
  selector: 'volontulo-offer-join-form',
  templateUrl: './offer-join-form.component.html'
})

export class OfferJoinFormComponent implements OnInit {
  public error;
  public communicate = 'Dodatkowe informacje dla organizatora (pole nieobowiązkowe)';
  public joinForm: FormGroup = this.fb.group({
    applicantEmail: [{value: '', disabled: true}],
    applicantName: [{value: '', disabled: true}],
    message: ['', [Validators.minLength(10), Validators.maxLength(2000)]],
    phoneNo: [{value: '', disabled: true}],
    honeyValue: [''],
  });
  public offerId: number;
  public submitEnabled = true;

  constructor(
    private activatedRoute: ActivatedRoute,
    private authService: AuthService,
    private fb: FormBuilder,
    private httpClient: HttpClient,
    private location: Location,
    private offersService: OffersService,
    private userService: UserService,
  ) {
  }

  ngOnInit() {
    this.authService.user$
      .subscribe(
        (user: User) => {
          this.joinForm.controls.applicantEmail.setValue(user.email);
          this.joinForm.controls.applicantName.setValue(this.userService.getFullName(user));
          this.joinForm.controls.phoneNo.setValue(user.phoneNo);
        }
      );

    this.activatedRoute.params
      .switchMap(params => this.offerId = params.offerId)
      .subscribe()
  }

  onSubmit() {
    if (this.joinForm.valid && !this.joinForm.value.honeyValue) {
      this.submitEnabled = false;

      this.offersService.joinOffer(this.offerId, this.joinForm.value.message).subscribe(
        response => {
          if (response.status === 201) {
            this.location.back()}},
            err => this.error = err.error.nonFieldErrors
      )
    }
  }
}