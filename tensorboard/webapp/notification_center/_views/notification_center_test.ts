/* Copyright 2021 The TensorFlow Authors. All Rights Reserved.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
==============================================================================*/
import {CommonModule} from '@angular/common';
import {TestBed} from '@angular/core/testing';
import {MatButtonModule} from '@angular/material/button';
import {MatMenuModule} from '@angular/material/menu';
import {By} from '@angular/platform-browser';
import {NoopAnimationsModule} from '@angular/platform-browser/animations';
import {MatIconTestingModule} from '../../testing/mat_icon_module';
import {NotificationCenterComponent} from './notification_center_component';
import {NotificationCenterContainer} from './notification_center_container';

describe('notification center', () => {
  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [
        CommonModule,
        MatButtonModule,
        MatMenuModule,
        MatIconTestingModule,
        NoopAnimationsModule,
      ],
      declarations: [NotificationCenterContainer, NotificationCenterComponent],
    }).compileComponents();
  });

  it('loads notification module', () => {
    const fixture = TestBed.createComponent(NotificationCenterContainer);
    fixture.detectChanges();

    const menuButton = fixture.debugElement.query(
      By.css('[aria-label="Display notification messages"]')
    );
    menuButton.nativeElement.click();
    fixture.detectChanges();

    const notificationMenu = fixture.debugElement.query(
      By.css('.notification-menu')
    );

    expect(notificationMenu).toBeTruthy();
    expect(
      notificationMenu.nativeNode.querySelector('.title').textContent
    ).toBe('2.4 release');
    expect(
      notificationMenu.nativeNode.querySelector('.category-icon').textContent
    ).toBe('info_outline_24px');
    expect(
      notificationMenu.nativeNode.querySelector('.content li').textContent
    ).toBe('Visualize Scalars, Images, and  Histograms in one place');
  });
});
