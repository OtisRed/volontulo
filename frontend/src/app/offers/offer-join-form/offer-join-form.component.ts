import {Component, OnInit} from '@angular/core';
import {FormBuilder, FormGroup, Validators} from '@angular/forms';
import {filter, take} from 'rxjs/operators';
import {User} from '../../user';
import {ActivatedRoute} from '@angular/router';
import {UserService} from '../../user.service';
import {AuthService} from '../../auth.service';

@Component({
  selector: 'volontulo-offer-join-form',
  templateUrl: './offer-join-form.component.html'
})

export class OfferJoinFormComponent implements OnInit {
  public joinForm: FormGroup = this.fb.group( {
    applicant_email: ['', [Validators.required, Validators.email]],
    applicant_name: ['', [Validators.required, Validators.minLength(3), Validators.maxLength(150)]],
    message: ['', [Validators.required, Validators.minLength(10), Validators.maxLength(2000)]],
    phone_no: ['', [Validators.maxLength(20)]],
    });

  public submitEnabled = false;

  constructor(
    private route: ActivatedRoute,
    private fb: FormBuilder,
    private authService: AuthService,
    private userService: UserService,
  ) {}

  ngOnInit() {
    this.authService.user$
      .pipe(
        filter(user => user !== null),
        take(1),
      )
      .subscribe(
        (user: User) => {
          this.joinForm.controls.applicant_email.setValue(user.email);
          this.joinForm.controls.applicant_name.setValue(this.userService.getFullName(user));
          this.joinForm.controls.phone_no.setValue(user.phoneNo);
        }
      )
  }

}
