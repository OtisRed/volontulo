import {Component, OnInit} from '@angular/core';
import {FormBuilder, FormGroup, Validators} from '@angular/forms';
import {catchError} from 'rxjs/operators';
import {User} from '../../user';
import {ActivatedRoute} from '@angular/router';
import {UserService} from '../../user.service';
import {AuthService} from '../../auth.service';
import {HttpClient} from "@angular/common/http";
import {environment} from "../../../environments/environment";
import { map, mergeMap } from 'rxjs/operators';
import {of} from "rxjs/observable/of";

@Component({
  selector: 'volontulo-offer-join-form',
  templateUrl: './offer-join-form.component.html'
})

export class OfferJoinFormComponent implements OnInit {
  public joinForm: FormGroup = this.fb.group( {
    applicant_email: ['', [Validators.required, Validators.email]],
    applicant_name: ['', [Validators.required, Validators.minLength(3), Validators.maxLength(150)]],
    message: ['', [Validators.minLength(10), Validators.maxLength(2000)]],
    phone_no: ['', [Validators.maxLength(20)]],
    });

  public submitEnabled = false;
  public success: null | boolean = null;

  constructor(
    private route: ActivatedRoute,
    private fb: FormBuilder,
    private authService: AuthService,
    private userService: UserService,
    private httpClient: HttpClient,
  ) {}

  ngOnInit() {
    this.authService.user$

      .subscribe(
        (user: User) => {
          this.joinForm.controls.applicant_email.setValue(user.email);
          this.joinForm.controls.applicant_name.setValue(this.userService.getFullName(user));
          this.joinForm.controls.phone_no.setValue(user.phoneNo);
        }
      )
  }

  onSubmit() {
    if (this.joinForm.valid) {
      console.log(this.joinForm.value)

      this.route.params.pipe(
        map(params => params.offerId),
        mergeMap(offerId => this.httpClient.post(`${environment.apiRoot}/offers/${offerId}/join`, this.joinForm.value)),
        catchError(err => {alert(err); return of(err)}))
        .subscribe(
        () => {this.success = true})
        }
  }
}
